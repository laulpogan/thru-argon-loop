#include "thru/trail_calendar.h"

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <limits>

namespace thru {

namespace {

constexpr double PI = 3.14159265358979323846;
constexpr double DEG2RAD = PI / 180.0;
constexpr double RAD2DEG = 180.0 / PI;

inline double deg_to_rad(double deg) noexcept {
    return deg * DEG2RAD;
}

inline double rad_to_deg(double rad) noexcept {
    return rad * RAD2DEG;
}

inline double fposmod(double x, double y) noexcept {
    return x - std::floor(x / y) * y;
}

inline double wrapf(double value, double min_val, double max_val) noexcept {
    double range = max_val - min_val;
    return value - range * std::floor((value - min_val) / range);
}

} // namespace

double TrailCalendar::utc_offset_hours(double julian_day) noexcept {
    return (julian_day >= DST_START_JD && julian_day < DST_END_JD) ? -7.0 : -8.0;
}

CivilDate TrailCalendar::civil(double julian_day) {
    double offset = utc_offset_hours(julian_day);
    double local = julian_day + offset / 24.0 + 0.5;
    int64_t z = static_cast<int64_t>(std::floor(local));
    double fraction = local - static_cast<double>(z);
    int64_t a = z;
    if (z >= 2299161) {
        int64_t alpha = static_cast<int64_t>(std::floor((static_cast<double>(z) - 1867216.25) / 36524.25));
        a = z + 1 + alpha - static_cast<int64_t>(std::floor(static_cast<double>(alpha) / 4.0));
    }
    int64_t b = a + 1524;
    int64_t c = static_cast<int64_t>(std::floor((static_cast<double>(b) - 122.1) / 365.25));
    int64_t d = static_cast<int64_t>(std::floor(365.25 * static_cast<double>(c)));
    int64_t e = static_cast<int64_t>(std::floor(static_cast<double>(b - d) / 30.6001));
    int day = static_cast<int>(b - d - static_cast<int64_t>(std::floor(30.6001 * static_cast<double>(e))));
    int month = static_cast<int>((e < 14) ? (e - 1) : (e - 13));
    int year = static_cast<int>((month > 2) ? (c - 4716) : (c - 4715));

    int raw_minutes = static_cast<int>(std::floor(fraction * 1440.0));
    int minutes = std::clamp(raw_minutes, 0, 1439);

    bool leap = ((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0);
    constexpr int starts[12] = {0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334};

    int clamped_month = std::clamp(month, 1, 12);
    int day_of_year = starts[clamped_month - 1] + day + ((leap && month > 2) ? 1 : 0);

    int weekday_idx = static_cast<int>((z % 7 + 7) % 7);

    CivilDate out;
    out.year = year;
    out.month = month;
    out.day = day;
    out.day_of_year = day_of_year;
    out.hour = minutes / 60;
    out.minute = minutes % 60;
    out.weekday = std::string(WEEKDAYS[static_cast<size_t>(weekday_idx)]);
    out.utc_offset = offset;
    out.month_name = std::string(MONTHS[static_cast<size_t>(clamped_month - 1)]);
    out.month_short = std::string(SHORT_MONTHS[static_cast<size_t>(clamped_month - 1)]);
    return out;
}

std::string TrailCalendar::label(double julian_day) {
    CivilDate d = civil(julian_day);
    char buf[64];
    std::snprintf(buf, sizeof(buf), "%s %d %s", d.weekday.c_str(), d.day, d.month_short.c_str());
    return std::string(buf);
}

std::string TrailCalendar::clock_label(double julian_day) {
    CivilDate d = civil(julian_day);
    char buf[16];
    std::snprintf(buf, sizeof(buf), "%02d:%02d", d.hour, d.minute);
    return std::string(buf);
}

HorizonCrossing TrailCalendar::horizon_crossing(double julian_day, double latitude, double longitude, double horizon_degrees) {
    double offset = utc_offset_hours(julian_day);
    // Local midnight that begins this civil day, expressed as a Julian day.
    double local_midnight = std::floor(julian_day + offset / 24.0 + 0.5) - 0.5 - offset / 24.0;
    double noon = local_midnight + 0.5;
    double n = noon - J2000;
    double anomaly = deg_to_rad(fposmod(357.529 + 0.98560028 * n, 360.0));
    double mean_longitude = fposmod(280.459 + 0.98564736 * n, 360.0);
    double ecliptic = deg_to_rad(mean_longitude + 1.915 * std::sin(anomaly) + 0.020 * std::sin(2.0 * anomaly));
    double obliquity = deg_to_rad(23.439 - 0.00000036 * n);
    double declination = std::asin(std::sin(obliquity) * std::sin(ecliptic));
    double right_ascension = rad_to_deg(std::atan2(std::cos(obliquity) * std::sin(ecliptic), std::cos(ecliptic)));
    // Equation of time in minutes: mean minus apparent right ascension.
    double equation_minutes = 4.0 * wrapf(mean_longitude - right_ascension, -180.0, 180.0);
    double phi = deg_to_rad(latitude);
    double cos_hour = (std::sin(deg_to_rad(horizon_degrees)) - std::sin(phi) * std::sin(declination)) /
                      (std::cos(phi) * std::cos(declination));
    double solar_noon_hours = 12.0 - longitude / 15.0 - equation_minutes / 60.0 + offset;

    HorizonCrossing crossing;
    crossing.noon = solar_noon_hours;
    crossing.declination = rad_to_deg(declination);
    crossing.rise = std::numeric_limits<double>::quiet_NaN();
    crossing.set = std::numeric_limits<double>::quiet_NaN();
    crossing.polar_day = false;
    crossing.polar_night = false;

    if (cos_hour <= -1.0) {
        crossing.polar_day = true;
        return crossing;
    }
    if (cos_hour >= 1.0) {
        crossing.polar_night = true;
        return crossing;
    }

    double half = rad_to_deg(std::acos(cos_hour)) / 15.0;
    crossing.rise = solar_noon_hours - half;
    crossing.set = solar_noon_hours + half;
    return crossing;
}

Daylight TrailCalendar::daylight(double julian_day, double latitude, double longitude) {
    HorizonCrossing crossing = horizon_crossing(julian_day, latitude, longitude, HORIZON_DEGREES);
    Daylight result;
    result.solar_noon = crossing.noon;
    result.declination = crossing.declination;

    if (crossing.polar_day) {
        result.sunrise = 0.0;
        result.sunset = 24.0;
        result.hours = 24.0;
        return result;
    }
    if (crossing.polar_night) {
        result.sunrise = crossing.noon;
        result.sunset = crossing.noon;
        result.hours = 0.0;
        return result;
    }

    result.sunrise = crossing.rise;
    result.sunset = crossing.set;
    result.hours = crossing.set - crossing.rise;
    return result;
}

AstronomicalTwilight TrailCalendar::astronomical_twilight(double julian_day, double latitude, double longitude) {
    HorizonCrossing crossing = horizon_crossing(julian_day, latitude, longitude, ASTRONOMICAL_DEGREES);
    AstronomicalTwilight result;
    result.dawn = crossing.rise;
    result.dusk = crossing.set;
    result.polar_day = crossing.polar_day;
    result.polar_night = crossing.polar_night;
    return result;
}

std::string TrailCalendar::hours_label(double hours) {
    if (std::isnan(hours)) {
        return "00:00";
    }
    double mod_hours = fposmod(hours, 24.0);
    int total_minutes = static_cast<int>(std::round(mod_hours * 60.0));
    int h = (total_minutes / 60) % 24;
    int m = total_minutes % 60;
    char buf[16];
    std::snprintf(buf, sizeof(buf), "%02d:%02d", h, m);
    return std::string(buf);
}

int TrailCalendar::weekday_index(std::string_view weekday) noexcept {
    for (size_t i = 0; i < WEEKDAYS.size(); ++i) {
        if (WEEKDAYS[i] == weekday) {
            return static_cast<int>(i);
        }
    }
    return -1;
}

} // namespace thru

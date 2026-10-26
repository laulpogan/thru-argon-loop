#include <doctest/doctest.h>
#include "thru/trail_calendar.h"

#include <cmath>

TEST_CASE("thru::TrailCalendar UTC offset and DST transitions") {
    // GDScript reference: godot/scripts/trail_calendar.gd:18
    // static func utc_offset_hours(julian_day: float) -> float:
    // US daylight time in 2026: [2026-03-08 10:00 UTC, 2026-11-01 09:00 UTC)
    // const DST_START_JD: float = 2461107.9166666665
    // const DST_END_JD: float = 2461345.875

    constexpr double dst_start = thru::TrailCalendar::DST_START_JD;
    constexpr double dst_end = thru::TrailCalendar::DST_END_JD;

    // Just before DST starts -> PST (-8.0)
    CHECK(thru::TrailCalendar::utc_offset_hours(dst_start - 1e-6) == -8.0);

    // Exactly at DST start -> PDT (-7.0)
    CHECK(thru::TrailCalendar::utc_offset_hours(dst_start) == -7.0);

    // Mid-summer (e.g. April 15, 2026) -> PDT (-7.0)
    CHECK(thru::TrailCalendar::utc_offset_hours(2461146.2916666665) == -7.0);

    // Just before DST ends -> PDT (-7.0)
    CHECK(thru::TrailCalendar::utc_offset_hours(dst_end - 1e-6) == -7.0);

    // Exactly at DST end -> PST (-8.0)
    CHECK(thru::TrailCalendar::utc_offset_hours(dst_end) == -8.0);

    // Winter (e.g. January 2026) -> PST (-8.0)
    CHECK(thru::TrailCalendar::utc_offset_hours(2461042.0) == -8.0);
}

TEST_CASE("thru::TrailCalendar civil date conversions") {
    // GDScript reference: godot/scripts/trail_calendar.gd:23
    // static func civil(julian_day: float) -> Dictionary
    // Test case from godot/tests/town_hours/check.gd:42:
    // Noon Pacific on Wed 15 Apr 2026: APRIL_JD = 2461146.2916666665
    constexpr double april_noon_jd = 2461146.2916666665;
    auto date = thru::TrailCalendar::civil(april_noon_jd);

    CHECK(date.year == 2026);
    CHECK(date.month == 4);
    CHECK(date.day == 15);
    CHECK(date.day_of_year == 105);
    CHECK(date.hour == 12);
    CHECK(date.minute == 0);
    CHECK(date.weekday == "Wed");
    CHECK(date.utc_offset == -7.0);
    CHECK(date.month_name == "April");
    CHECK(date.month_short == "Apr");

    // GDScript reference: godot/tests/town_hours/check.gd:46
    // WED_0700 = APRIL_JD - 5.0 / 24.0 + 0.5 / 1440.0
    constexpr double wed_0700_jd = april_noon_jd - 5.0 / 24.0 + 0.5 / 1440.0;
    auto date_0700 = thru::TrailCalendar::civil(wed_0700_jd);
    CHECK(date_0700.hour == 7);
    CHECK(date_0700.minute == 0);
    CHECK(date_0700.weekday == "Wed");

    // GDScript reference: godot/tests/town_hours/check.gd:49
    // SUNDAY_1330 = APRIL_JD + 4.0 + 1.5 / 24.0 + 0.5 / 1440.0
    constexpr double sun_1330_jd = april_noon_jd + 4.0 + 1.5 / 24.0 + 0.5 / 1440.0;
    auto date_1330 = thru::TrailCalendar::civil(sun_1330_jd);
    CHECK(date_1330.year == 2026);
    CHECK(date_1330.month == 4);
    CHECK(date_1330.day == 19);
    CHECK(date_1330.hour == 13);
    CHECK(date_1330.minute == 30);
    CHECK(date_1330.weekday == "Sun");

    // Leap year checks: 2024 is a leap year
    // Feb 29, 2024 at midnight local PST
    constexpr double leap_feb29 = 2460369.5 + 8.0 / 24.0;
    auto date_leap29 = thru::TrailCalendar::civil(leap_feb29);
    CHECK(date_leap29.year == 2024);
    CHECK(date_leap29.month == 2);
    CHECK(date_leap29.day == 29);
    CHECK(date_leap29.day_of_year == 60);

    // Mar 1, 2024 in leap year -> day_of_year = 61
    constexpr double leap_mar01 = 2460370.5 + 8.0 / 24.0;
    auto date_leap_mar = thru::TrailCalendar::civil(leap_mar01);
    CHECK(date_leap_mar.year == 2024);
    CHECK(date_leap_mar.month == 3);
    CHECK(date_leap_mar.day == 1);
    CHECK(date_leap_mar.day_of_year == 61);
}

TEST_CASE("thru::TrailCalendar labels and formatting") {
    // GDScript reference: godot/scripts/trail_calendar.gd:43
    // static func label(julian_day: float) -> String:
    // GDScript reference: godot/scripts/trail_calendar.gd:49
    // static func clock_label(julian_day: float) -> String:
    // GDScript reference: godot/scripts/trail_calendar.gd:124
    // static func hours_label(hours: float) -> String:
    constexpr double april_noon_jd = 2461146.2916666665;
    CHECK(thru::TrailCalendar::label(april_noon_jd) == "Wed 15 Apr");
    CHECK(thru::TrailCalendar::clock_label(april_noon_jd) == "12:00");

    // Check Sunday 19 Apr labels
    constexpr double sun_1000_jd = april_noon_jd + 4.0 - 2.0 / 24.0 + 0.5 / 1440.0;
    CHECK(thru::TrailCalendar::label(sun_1000_jd) == "Sun 19 Apr");
    CHECK(thru::TrailCalendar::clock_label(sun_1000_jd) == "10:00");

    // hours_label formatting and wrap behavior
    CHECK(thru::TrailCalendar::hours_label(0.0) == "00:00");
    CHECK(thru::TrailCalendar::hours_label(6.666666666666667) == "06:40");
    CHECK(thru::TrailCalendar::hours_label(12.5) == "12:30");
    CHECK(thru::TrailCalendar::hours_label(23.9999) == "00:00");
    CHECK(thru::TrailCalendar::hours_label(25.5) == "01:30");
    CHECK(thru::TrailCalendar::hours_label(-1.0) == "23:00");
    CHECK(thru::TrailCalendar::hours_label(std::numeric_limits<double>::quiet_NaN()) == "00:00");
}

TEST_CASE("thru::TrailCalendar daylight calculations") {
    // GDScript reference: godot/scripts/trail_calendar.gd:55
    // static func daylight(julian_day: float, latitude: float, longitude: float) -> Dictionary:
    // Test observer at lat=36.0, lon=-119.0 on April 15 2026
    constexpr double april_noon_jd = 2461146.2916666665;
    auto light = thru::TrailCalendar::daylight(april_noon_jd, 36.0, -119.0);

    // Tolerances: within 0.001 hours (~3.6 seconds)
    CHECK(doctest::Approx(light.solar_noon).epsilon(0.001) == 12.93289);
    CHECK(doctest::Approx(light.sunrise).epsilon(0.001) == 6.37305);
    CHECK(doctest::Approx(light.sunset).epsilon(0.001) == 19.49273);
    CHECK(doctest::Approx(light.hours).epsilon(0.001) == 13.11968);
    CHECK(doctest::Approx(light.declination).epsilon(0.001) == 9.97608);

    // String formatting check: sunrise 06:22, sunset 19:30
    CHECK(thru::TrailCalendar::hours_label(light.sunrise) == "06:22");
    CHECK(thru::TrailCalendar::hours_label(light.sunset) == "19:30");

    // Polar day test (Arctic summer lat 80.0, June 21, 2026 ~ JD 2461213.0)
    // GDScript reference: godot/scripts/trail_calendar.gd:58
    auto polar_day_light = thru::TrailCalendar::daylight(2461213.0, 80.0, 0.0);
    CHECK(polar_day_light.sunrise == 0.0);
    CHECK(polar_day_light.sunset == 24.0);
    CHECK(polar_day_light.hours == 24.0);

    // Polar night test (Arctic winter lat 80.0, Dec 21, 2025 ~ JD 2461025.0)
    // GDScript reference: godot/scripts/trail_calendar.gd:61
    auto polar_night_light = thru::TrailCalendar::daylight(2461025.0, 80.0, 0.0);
    CHECK(polar_night_light.sunrise == polar_night_light.solar_noon);
    CHECK(polar_night_light.sunset == polar_night_light.solar_noon);
    CHECK(polar_night_light.hours == 0.0);
}

TEST_CASE("thru::TrailCalendar astronomical twilight") {
    // GDScript reference: godot/scripts/trail_calendar.gd:68
    // static func astronomical_twilight(julian_day: float, latitude: float, longitude: float) -> Dictionary:
    // GDScript reference: godot/tests/satellites/check.gd:57
    constexpr double april_noon_jd = 2461146.2916666665;
    auto twilight = thru::TrailCalendar::astronomical_twilight(april_noon_jd, 36.0, -119.0);

    CHECK_FALSE(twilight.polar_day);
    CHECK_FALSE(twilight.polar_night);
    CHECK(doctest::Approx(twilight.dawn).epsilon(0.001) == 4.86360);
    CHECK(doctest::Approx(twilight.dusk).epsilon(0.001) == 21.00218);

    CHECK(thru::TrailCalendar::hours_label(twilight.dawn) == "04:52");
    CHECK(thru::TrailCalendar::hours_label(twilight.dusk) == "21:00");

    // Polar day twilight (lat 80.0 in summer: Sun never dips 18 deg below horizon)
    auto polar_day_twilight = thru::TrailCalendar::astronomical_twilight(2461213.0, 80.0, 0.0);
    CHECK(polar_day_twilight.polar_day);
    CHECK(std::isnan(polar_day_twilight.dawn));
    CHECK(std::isnan(polar_day_twilight.dusk));

    // Polar night twilight (lat 88.0 in winter: Sun never rises above -18 deg)
    auto polar_night_twilight = thru::TrailCalendar::astronomical_twilight(2461025.0, 88.0, 0.0);
    CHECK(polar_night_twilight.polar_night);
    CHECK(std::isnan(polar_night_twilight.dawn));
    CHECK(std::isnan(polar_night_twilight.dusk));
}

TEST_CASE("thru::TrailCalendar weekday and month lookup tables") {
    // GDScript reference: godot/scripts/trail_calendar.gd:5-7
    CHECK(thru::TrailCalendar::MONTHS.size() == 12);
    CHECK(thru::TrailCalendar::SHORT_MONTHS.size() == 12);
    CHECK(thru::TrailCalendar::WEEKDAYS.size() == 7);

    CHECK(thru::TrailCalendar::MONTHS[0] == "January");
    CHECK(thru::TrailCalendar::MONTHS[11] == "December");
    CHECK(thru::TrailCalendar::SHORT_MONTHS[0] == "Jan");
    CHECK(thru::TrailCalendar::SHORT_MONTHS[11] == "Dec");
    CHECK(thru::TrailCalendar::WEEKDAYS[0] == "Mon");
    CHECK(thru::TrailCalendar::WEEKDAYS[6] == "Sun");

    CHECK(thru::TrailCalendar::weekday_index("Mon") == 0);
    CHECK(thru::TrailCalendar::weekday_index("Wed") == 2);
    CHECK(thru::TrailCalendar::weekday_index("Sun") == 6);
    CHECK(thru::TrailCalendar::weekday_index("Invalid") == -1);
}

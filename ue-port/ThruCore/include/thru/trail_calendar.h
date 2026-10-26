#pragma once

#include <array>
#include <cmath>
#include <cstdint>
#include <string>
#include <string_view>

namespace thru {

struct CivilDate {
    int year{0};
    int month{0};            // 1..12
    int day{0};              // 1..31
    int day_of_year{0};      // 1..366
    int hour{0};             // 0..23
    int minute{0};           // 0..59
    std::string weekday;     // "Mon", "Tue", ...
    double utc_offset{0.0};  // Pacific clock offset in hours (-7.0 or -8.0)
    std::string month_name;  // "January", ...
    std::string month_short; // "Jan", ...
};

struct Daylight {
    double sunrise{0.0};     // Civil clock hours
    double sunset{0.0};      // Civil clock hours
    double solar_noon{0.0};  // Civil clock hours
    double hours{0.0};       // Daylight duration in hours
    double declination{0.0}; // Solar declination in degrees
};

struct AstronomicalTwilight {
    double dawn{0.0};        // Civil clock hours
    double dusk{0.0};        // Civil clock hours
    bool polar_day{false};
    bool polar_night{false};
};

struct HorizonCrossing {
    double noon{0.0};
    double declination{0.0};
    double rise{0.0};
    double set{0.0};
    bool polar_day{false};
    bool polar_night{false};
};

class TrailCalendar {
public:
    using CivilDate = thru::CivilDate;
    using Daylight = thru::Daylight;
    using AstronomicalTwilight = thru::AstronomicalTwilight;
    using HorizonCrossing = thru::HorizonCrossing;

    static constexpr std::array<std::string_view, 12> MONTHS = {
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    };

    static constexpr std::array<std::string_view, 12> SHORT_MONTHS = {
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    };

    static constexpr std::array<std::string_view, 7> WEEKDAYS = {
        "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"
    };

    /// US daylight time in 2026 runs from 2026-03-08 10:00 UTC to 2026-11-01 09:00 UTC.
    static constexpr double DST_START_JD = 2461107.9166666665;
    static constexpr double DST_END_JD = 2461345.875;

    /// Sun's centre 0.833 degrees below the horizon: refraction plus the solar radius.
    static constexpr double HORIZON_DEGREES = -0.833;

    /// Sun's centre 18 degrees below the horizon: astronomical twilight.
    static constexpr double ASTRONOMICAL_DEGREES = -18.0;

    /// J2000 epoch Julian day.
    static constexpr double J2000 = 2451545.0;

    /// Pacific clock offset from UTC in hours for this instant (PDT -7 or PST -8).
    static double utc_offset_hours(double julian_day) noexcept;

    /// Gregorian civil date at the Pacific clock (Meeus, Astronomical Algorithms ch. 7).
    static CivilDate civil(double julian_day);

    /// "Mon 20 Apr" style label for the HUD.
    static std::string label(double julian_day);

    /// Clock time "06:40" at the Pacific clock.
    static std::string clock_label(double julian_day);

    /// Sunrise, sunset and day length for the civil day containing julian_day.
    static Daylight daylight(double julian_day, double latitude, double longitude);

    /// Instants of astronomical twilight (18 degrees solar depression).
    static AstronomicalTwilight astronomical_twilight(double julian_day, double latitude, double longitude);

    /// Horizon crossing calculation at an arbitrary horizon altitude angle.
    static HorizonCrossing horizon_crossing(double julian_day, double latitude, double longitude, double horizon_degrees);

    /// Format hours float (e.g. 6.6666) to "HH:MM" string format with 24h wrapping.
    static std::string hours_label(double hours);

    /// Helper to find index in WEEKDAYS (0 for Mon .. 6 for Sun, or -1 if not found).
    static int weekday_index(std::string_view weekday) noexcept;
};

} // namespace thru

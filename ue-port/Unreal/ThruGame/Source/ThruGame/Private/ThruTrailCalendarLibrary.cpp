#include "ThruTrailCalendarLibrary.h"

double UThruTrailCalendarLibrary::UtcOffsetHours(double JulianDay)
{
    return thru::TrailCalendar::utc_offset_hours(JulianDay);
}

FThruCivilDate UThruTrailCalendarLibrary::Civil(double JulianDay)
{
    return FThruCivilDate::FromCore(thru::TrailCalendar::civil(JulianDay));
}

FString UThruTrailCalendarLibrary::Label(double JulianDay)
{
    return FString(UTF8_TO_TCHAR(thru::TrailCalendar::label(JulianDay).c_str()));
}

FString UThruTrailCalendarLibrary::ClockLabel(double JulianDay)
{
    return FString(UTF8_TO_TCHAR(thru::TrailCalendar::clock_label(JulianDay).c_str()));
}

FThruDaylight UThruTrailCalendarLibrary::Daylight(double JulianDay, double Latitude, double Longitude)
{
    return FThruDaylight::FromCore(thru::TrailCalendar::daylight(JulianDay, Latitude, Longitude));
}

FThruAstronomicalTwilight UThruTrailCalendarLibrary::AstronomicalTwilight(double JulianDay, double Latitude, double Longitude)
{
    return FThruAstronomicalTwilight::FromCore(thru::TrailCalendar::astronomical_twilight(JulianDay, Latitude, Longitude));
}

FString UThruTrailCalendarLibrary::HoursLabel(double Hours)
{
    return FString(UTF8_TO_TCHAR(thru::TrailCalendar::hours_label(Hours).c_str()));
}

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "thru/trail_calendar.h"
#include "ThruTrailCalendarLibrary.generated.h"

USTRUCT(BlueprintType)
struct THRUGAME_API FThruCivilDate
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    int32 Year = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    int32 Month = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    int32 Day = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    int32 DayOfYear = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    int32 Hour = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    int32 Minute = 0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    FString Weekday;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    double UtcOffset = 0.0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    FString MonthName;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    FString MonthShort;

    static FThruCivilDate FromCore(const thru::CivilDate& Core)
    {
        FThruCivilDate Out;
        Out.Year = Core.year;
        Out.Month = Core.month;
        Out.Day = Core.day;
        Out.DayOfYear = Core.day_of_year;
        Out.Hour = Core.hour;
        Out.Minute = Core.minute;
        Out.Weekday = UTF8_TO_TCHAR(Core.weekday.c_str());
        Out.UtcOffset = Core.utc_offset;
        Out.MonthName = UTF8_TO_TCHAR(Core.month_name.c_str());
        Out.MonthShort = UTF8_TO_TCHAR(Core.month_short.c_str());
        return Out;
    }
};

USTRUCT(BlueprintType)
struct THRUGAME_API FThruDaylight
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    double Sunrise = 0.0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    double Sunset = 0.0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    double SolarNoon = 0.0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    double Hours = 0.0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    double Declination = 0.0;

    static FThruDaylight FromCore(const thru::Daylight& Core)
    {
        FThruDaylight Out;
        Out.Sunrise = Core.sunrise;
        Out.Sunset = Core.sunset;
        Out.SolarNoon = Core.solar_noon;
        Out.Hours = Core.hours;
        Out.Declination = Core.declination;
        return Out;
    }
};

USTRUCT(BlueprintType)
struct THRUGAME_API FThruAstronomicalTwilight
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    double Dawn = 0.0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    double Dusk = 0.0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    bool bPolarDay = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Calendar")
    bool bPolarNight = false;

    static FThruAstronomicalTwilight FromCore(const thru::AstronomicalTwilight& Core)
    {
        FThruAstronomicalTwilight Out;
        Out.Dawn = Core.dawn;
        Out.Dusk = Core.dusk;
        Out.bPolarDay = Core.polar_day;
        Out.bPolarNight = Core.polar_night;
        return Out;
    }
};

/**
 * Blueprint library exposing civil calendar, solar daylight, and twilight calculations.
 */
UCLASS()
class THRUGAME_API UThruTrailCalendarLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintPure, Category = "Calendar")
    static double UtcOffsetHours(double JulianDay);

    UFUNCTION(BlueprintPure, Category = "Calendar")
    static FThruCivilDate Civil(double JulianDay);

    UFUNCTION(BlueprintPure, Category = "Calendar")
    static FString Label(double JulianDay);

    UFUNCTION(BlueprintPure, Category = "Calendar")
    static FString ClockLabel(double JulianDay);

    UFUNCTION(BlueprintPure, Category = "Calendar")
    static FThruDaylight Daylight(double JulianDay, double Latitude, double Longitude);

    UFUNCTION(BlueprintPure, Category = "Calendar")
    static FThruAstronomicalTwilight AstronomicalTwilight(double JulianDay, double Latitude, double Longitude);

    UFUNCTION(BlueprintPure, Category = "Calendar")
    static FString HoursLabel(double Hours);
};

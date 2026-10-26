#include "ThruCelestialEphemeris.h"

bool UThruCelestialEphemeris::LoadDefault()
{
    return CoreEphemeris.load_default();
}

bool UThruCelestialEphemeris::LoadPath(const FString& Path)
{
    const std::string PathUtf8 = TCHAR_TO_UTF8(*Path);
    return CoreEphemeris.load(PathUtf8);
}

bool UThruCelestialEphemeris::LoadString(const FString& Content)
{
    const std::string ContentUtf8 = TCHAR_TO_UTF8(*Content);
    return CoreEphemeris.load_from_string(ContentUtf8);
}

bool UThruCelestialEphemeris::IsValid() const
{
    return CoreEphemeris.is_valid();
}

FString UThruCelestialEphemeris::GetProblem() const
{
    return FString(UTF8_TO_TCHAR(CoreEphemeris.problem().c_str()));
}

int32 UThruCelestialEphemeris::GetSampleCount() const
{
    return static_cast<int32>(CoreEphemeris.size());
}

FThruCelestialSample UThruCelestialEphemeris::Sample(const FString& Body, double JulianDay) const
{
    const std::string BodyUtf8 = TCHAR_TO_UTF8(*Body);
    return FThruCelestialSample::FromCore(CoreEphemeris.sample(BodyUtf8, JulianDay));
}

FVector UThruCelestialEphemeris::MoonToSunDirection(
    const FVector& SunEquatorial,
    double SunDistanceAu,
    const FVector& MoonEquatorial,
    double MoonDistanceAu
)
{
    const thru::Vector3 Sun(SunEquatorial.X, SunEquatorial.Y, SunEquatorial.Z);
    const thru::Vector3 Moon(MoonEquatorial.X, MoonEquatorial.Y, MoonEquatorial.Z);
    const thru::Vector3 Result = thru::CelestialEphemeris::moon_to_sun_direction(Sun, SunDistanceAu, Moon, MoonDistanceAu);
    return FVector(Result.x, Result.y, Result.z);
}

double UThruCelestialEphemeris::MoonIlluminatedFraction(
    const FVector& SunEquatorial,
    double SunDistanceAu,
    const FVector& MoonEquatorial,
    double MoonDistanceAu
)
{
    const thru::Vector3 Sun(SunEquatorial.X, SunEquatorial.Y, SunEquatorial.Z);
    const thru::Vector3 Moon(MoonEquatorial.X, MoonEquatorial.Y, MoonEquatorial.Z);
    return thru::CelestialEphemeris::moon_illuminated_fraction(Sun, SunDistanceAu, Moon, MoonDistanceAu);
}

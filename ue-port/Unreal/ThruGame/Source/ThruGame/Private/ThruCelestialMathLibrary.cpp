#include "ThruCelestialMathLibrary.h"

FVector UThruCelestialMathLibrary::EquatorialVector(double RaDegrees, double DecDegrees)
{
    const thru::Vector3 Result = thru::CelestialMath::equatorial_vector(RaDegrees, DecDegrees);
    return FVector(Result.x, Result.y, Result.z);
}

FVector UThruCelestialMathLibrary::HorizontalDirection(const FVector& Equatorial, double JulianDay, double Latitude, double Longitude)
{
    const thru::Vector3 CoreEquatorial(Equatorial.X, Equatorial.Y, Equatorial.Z);
    const thru::Vector3 Result = thru::CelestialMath::horizontal_direction(CoreEquatorial, JulianDay, Latitude, Longitude);
    return FVector(Result.x, Result.y, Result.z);
}

FThruBasis UThruCelestialMathLibrary::J2000HorizontalBasis(double JulianDay, double Latitude, double Longitude)
{
    return FThruBasis::FromCore(thru::CelestialMath::j2000_horizontal_basis(JulianDay, Latitude, Longitude));
}

FThruBasis UThruCelestialMathLibrary::HorizonBasis(double JulianDay, double Latitude, double Longitude)
{
    return FThruBasis::FromCore(thru::CelestialMath::horizon_basis(JulianDay, Latitude, Longitude));
}

FThruBasis UThruCelestialMathLibrary::PrecessionBasis(double JulianDay)
{
    return FThruBasis::FromCore(thru::CelestialMath::precession_basis(JulianDay));
}

double UThruCelestialMathLibrary::ApparentSiderealDegrees(double JulianDay)
{
    return thru::CelestialMath::apparent_sidereal_degrees(JulianDay);
}

FVector UThruCelestialMathLibrary::TopocentricEquatorial(
    const FVector& Geocentric,
    double DistanceAu,
    double JulianDay,
    double Latitude,
    double Longitude,
    double ElevationMetres
)
{
    const thru::Vector3 CoreGeocentric(Geocentric.X, Geocentric.Y, Geocentric.Z);
    const thru::Vector3 Result = thru::CelestialMath::topocentric_equatorial(
        CoreGeocentric,
        DistanceAu,
        JulianDay,
        Latitude,
        Longitude,
        ElevationMetres
    );
    return FVector(Result.x, Result.y, Result.z);
}

double UThruCelestialMathLibrary::Azimuth(const FVector& Direction)
{
    const thru::Vector3 CoreDirection(Direction.X, Direction.Y, Direction.Z);
    return thru::CelestialMath::azimuth(CoreDirection);
}

double UThruCelestialMathLibrary::Altitude(const FVector& Direction)
{
    const thru::Vector3 CoreDirection(Direction.X, Direction.Y, Direction.Z);
    return thru::CelestialMath::altitude(CoreDirection);
}

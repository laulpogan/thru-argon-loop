#include "thru/celestial_math.h"
#include <cmath>

namespace thru {

Vector3 CelestialMath::equatorial_vector(double ra_degrees, double dec_degrees) {
    const double ra = deg_to_rad(ra_degrees);
    const double dec = deg_to_rad(dec_degrees);
    const double cos_dec = std::cos(dec);
    return Vector3(cos_dec * std::cos(ra), cos_dec * std::sin(ra), std::sin(dec)).normalized();
}

Vector3 CelestialMath::horizontal_direction(const Vector3& equatorial, double julian_day, double latitude, double longitude) {
    return (horizon_basis(julian_day, latitude, longitude) * equatorial).normalized();
}

Basis CelestialMath::j2000_horizontal_basis(double julian_day, double latitude, double longitude) {
    return horizon_basis(julian_day, latitude, longitude) * precession_basis(julian_day);
}

Basis CelestialMath::horizon_basis(double julian_day, double latitude, double longitude) {
    const double sidereal = deg_to_rad(apparent_sidereal_degrees(julian_day) + longitude);
    const double phi = deg_to_rad(latitude);
    const double sin_sidereal = std::sin(sidereal);
    const double cos_sidereal = std::cos(sidereal);
    const double sin_phi = std::sin(phi);
    const double cos_phi = std::cos(phi);
    return Basis(
        Vector3(-sin_sidereal, cos_phi * cos_sidereal, sin_phi * cos_sidereal),
        Vector3(cos_sidereal, cos_phi * sin_sidereal, sin_phi * sin_sidereal),
        Vector3(0.0, sin_phi, -cos_phi)
    );
}

Basis CelestialMath::precession_basis(double julian_day) {
    const Vector3 x = precess_vector(Vector3::right(), julian_day);
    const Vector3 y = precess_vector(Vector3::up(), julian_day);
    const Vector3 z = precess_vector(Vector3::back(), julian_day);
    return Basis(x, y, z).orthonormalized();
}

double CelestialMath::apparent_sidereal_degrees(double julian_day) {
    // USNO's 2000-2100 expression is accurate to about 0.1 second of sidereal time.
    const double midnight = std::floor(julian_day - 0.5) + 0.5;
    const double hours = (julian_day - midnight) * 24.0;
    const double days_midnight = midnight - J2000;
    const double days_tt = julian_day - J2000;
    const double centuries = days_tt / 36525.0;
    const double gmst_hours = fposmod(
        6.697375 + 0.065709824279 * days_midnight + 1.0027379 * hours
        + 0.0000258 * centuries * centuries,
        24.0
    );
    const double omega = deg_to_rad(125.04 - 0.052954 * days_tt);
    const double sun_longitude = deg_to_rad(280.47 + 0.98565 * days_tt);
    const double obliquity = deg_to_rad(23.4393 - 0.0000004 * days_tt);
    const double nutation_hours = -0.000319 * std::sin(omega) - 0.000024 * std::sin(2.0 * sun_longitude);
    const double equation_of_equinoxes = nutation_hours * std::cos(obliquity);
    return fposmod((gmst_hours + equation_of_equinoxes) * 15.0, 360.0);
}

Vector3 CelestialMath::topocentric_equatorial(
    const Vector3& geocentric,
    double distance_au,
    double julian_day,
    double latitude,
    double longitude,
    double elevation_metres
) {
    if (distance_au <= EARTH_EQUATORIAL_RADIUS_AU) {
        return geocentric.normalized();
    }
    const double ra = std::atan2(geocentric.y, geocentric.x);
    const double dec = std::asin(std::clamp(geocentric.z, -1.0, 1.0));
    const double phi = deg_to_rad(latitude);
    const double u = std::atan(EARTH_FLATTENING_RATIO * std::tan(phi));
    const double height_ratio = elevation_metres / 6378140.0;
    const double rho_sin = EARTH_FLATTENING_RATIO * std::sin(u) + height_ratio * std::sin(phi);
    const double rho_cos = std::cos(u) + height_ratio * std::cos(phi);
    const double parallax = std::asin(EARTH_EQUATORIAL_RADIUS_AU / distance_au);
    const double hour_angle = deg_to_rad(apparent_sidereal_degrees(julian_day) + longitude) - ra;
    const double delta_ra = std::atan2(
        -rho_cos * std::sin(parallax) * std::sin(hour_angle),
        std::cos(dec) - rho_cos * std::sin(parallax) * std::cos(hour_angle)
    );
    const double topocentric_ra = ra + delta_ra;
    const double topocentric_dec = std::atan2(
        (std::sin(dec) - rho_sin * std::sin(parallax)) * std::cos(delta_ra),
        std::cos(dec) - rho_cos * std::sin(parallax) * std::cos(hour_angle)
    );
    return equatorial_vector(rad_to_deg(topocentric_ra), rad_to_deg(topocentric_dec));
}

Vector3 CelestialMath::precess_vector(const Vector3& source, double julian_day) {
    // IAU 1976 precession is sub-arcminute across the fixed 2026 campaign year.
    const double centuries = (julian_day - J2000) / 36525.0;
    const double zeta = deg_to_rad((2306.2181 * centuries + 0.30188 * centuries * centuries
        + 0.017998 * centuries * centuries * centuries) / 3600.0);
    const double zed = deg_to_rad((2306.2181 * centuries + 1.09468 * centuries * centuries
        + 0.018203 * centuries * centuries * centuries) / 3600.0);
    const double theta = deg_to_rad((2004.3109 * centuries - 0.42665 * centuries * centuries
        - 0.041833 * centuries * centuries * centuries) / 3600.0);
    const double ra = std::atan2(source.y, source.x);
    const double dec = std::asin(std::clamp(source.z, -1.0, 1.0));
    const double a = std::cos(dec) * std::sin(ra + zeta);
    const double b = std::cos(theta) * std::cos(dec) * std::cos(ra + zeta) - std::sin(theta) * std::sin(dec);
    const double c = std::sin(theta) * std::cos(dec) * std::cos(ra + zeta) + std::cos(theta) * std::sin(dec);
    const double destination_ra = std::atan2(a, b) + zed;
    const double destination_dec = std::asin(std::clamp(c, -1.0, 1.0));
    return equatorial_vector(rad_to_deg(destination_ra), rad_to_deg(destination_dec));
}

} // namespace thru

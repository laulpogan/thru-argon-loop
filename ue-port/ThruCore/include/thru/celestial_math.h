#pragma once

#include <cmath>
#include <algorithm>

namespace thru {

struct Vector3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};

    constexpr Vector3() = default;
    constexpr Vector3(double in_x, double in_y, double in_z) : x(in_x), y(in_y), z(in_z) {}

    static constexpr Vector3 right() { return Vector3(1.0, 0.0, 0.0); }
    static constexpr Vector3 up() { return Vector3(0.0, 1.0, 0.0); }
    static constexpr Vector3 back() { return Vector3(0.0, 0.0, 1.0); }

    Vector3 operator+(const Vector3& o) const { return Vector3(x + o.x, y + o.y, z + o.z); }
    Vector3 operator-(const Vector3& o) const { return Vector3(x - o.x, y - o.y, z - o.z); }
    Vector3 operator-() const { return Vector3(-x, -y, -z); }
    Vector3 operator*(double s) const { return Vector3(x * s, y * s, z * s); }
    Vector3 operator/(double s) const { return Vector3(x / s, y / s, z / s); }
    friend Vector3 operator*(double s, const Vector3& v) { return Vector3(s * v.x, s * v.y, s * v.z); }

    bool operator==(const Vector3& o) const { return x == o.x && y == o.y && z == o.z; }
    bool operator!=(const Vector3& o) const { return !(*this == o); }

    double length_squared() const { return x * x + y * y + z * z; }
    double length() const { return std::sqrt(length_squared()); }
    double dot(const Vector3& o) const { return x * o.x + y * o.y + z * o.z; }
    Vector3 cross(const Vector3& o) const {
        return Vector3(
            y * o.z - z * o.y,
            z * o.x - x * o.z,
            x * o.y - y * o.x
        );
    }

    Vector3 normalized() const {
        const double l = length();
        return (l > 0.0) ? (*this / l) : Vector3();
    }

    Vector3 slerp(const Vector3& to, double weight) const {
        const double d = std::clamp(dot(to), -1.0, 1.0);
        const double theta = std::acos(d);
        const double sin_theta = std::sin(theta);
        if (sin_theta < 1e-6) {
            return ((*this) * (1.0 - weight) + to * weight).normalized();
        }
        const double w0 = std::sin((1.0 - weight) * theta) / sin_theta;
        const double w1 = std::sin(weight * theta) / sin_theta;
        return ((*this) * w0 + to * w1).normalized();
    }
};

struct Basis {
    Vector3 x{1.0, 0.0, 0.0}; // Column 0 (x-axis)
    Vector3 y{0.0, 1.0, 0.0}; // Column 1 (y-axis)
    Vector3 z{0.0, 0.0, 1.0}; // Column 2 (z-axis)

    constexpr Basis() = default;
    constexpr Basis(const Vector3& in_x, const Vector3& in_y, const Vector3& in_z)
        : x(in_x), y(in_y), z(in_z) {}

    Vector3 operator*(const Vector3& v) const {
        return Vector3(
            v.x * x.x + v.y * y.x + v.z * z.x,
            v.x * x.y + v.y * y.y + v.z * z.y,
            v.x * x.z + v.y * y.z + v.z * z.z
        );
    }

    Basis operator*(const Basis& b) const {
        return Basis((*this) * b.x, (*this) * b.y, (*this) * b.z);
    }

    Basis orthonormalized() const {
        const Vector3 nx = x.normalized();
        const Vector3 ny = (y - nx * nx.dot(y)).normalized();
        const Vector3 nz = (z - nx * nx.dot(z) - ny * ny.dot(z)).normalized();
        return Basis(nx, ny, nz);
    }
};

class CelestialMath {
public:
    static constexpr double J2000 = 2451545.0;
    static constexpr double EARTH_EQUATORIAL_RADIUS_AU = 4.263521e-5;
    static constexpr double EARTH_FLATTENING_RATIO = 0.99664719;
    static constexpr double PI = 3.14159265358979323846;

    static Vector3 equatorial_vector(double ra_degrees, double dec_degrees);
    static Vector3 horizontal_direction(const Vector3& equatorial, double julian_day, double latitude, double longitude);
    static Basis j2000_horizontal_basis(double julian_day, double latitude, double longitude);
    static Basis horizon_basis(double julian_day, double latitude, double longitude);
    static Basis precession_basis(double julian_day);
    static double apparent_sidereal_degrees(double julian_day);
    static Vector3 topocentric_equatorial(
        const Vector3& geocentric,
        double distance_au,
        double julian_day,
        double latitude,
        double longitude,
        double elevation_metres = 0.0
    );

    // Coordinate conversion and utility helpers
    static constexpr double deg_to_rad(double degrees) {
        return degrees * (PI / 180.0);
    }

    static constexpr double rad_to_deg(double radians) {
        return radians * (180.0 / PI);
    }

    static inline double fposmod(double x, double y) {
        if (y == 0.0) return 0.0;
        double r = std::fmod(x, y);
        if ((r < 0.0 && y > 0.0) || (r > 0.0 && y < 0.0)) {
            r += y;
        }
        if (y > 0.0 && r >= y) {
            r = 0.0;
        }
        return r;
    }

    static inline double azimuth(const Vector3& direction) {
        return fposmod(rad_to_deg(std::atan2(direction.x, -direction.z)), 360.0);
    }

    static inline double altitude(const Vector3& direction) {
        return rad_to_deg(std::asin(std::clamp(direction.y, -1.0, 1.0)));
    }

private:
    static Vector3 precess_vector(const Vector3& source, double julian_day);
};

} // namespace thru

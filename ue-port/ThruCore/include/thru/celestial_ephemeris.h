#pragma once

#include <string>
#include <vector>
#include <cstddef>
#include <nlohmann/json.hpp>
#include "thru/celestial_math.h"
#include "thru/data_source.h"

namespace thru {

struct CelestialSample {
    Vector3 equatorial{0.0, 0.0, 0.0};
    double distance_au{0.0};
    bool interpolated{false};
    bool valid{false};
};

class CelestialEphemeris {
public:
    static constexpr const char* DEFAULT_PATH = "data/celestial/sun_moon_2026.tsv";

    CelestialEphemeris() = default;

    static CelestialEphemeris load_default(const DataSource* data_source = nullptr);
    static CelestialEphemeris load_path(const std::string& path, const DataSource* data_source = nullptr);
    static CelestialEphemeris load_string(const std::string& content);
    static CelestialEphemeris load_json(const nlohmann::json& j);

    bool is_valid() const { return problem_.empty(); }
    const std::string& problem() const { return problem_; }
    size_t size() const { return jds_.size(); }

    CelestialSample sample(const std::string& body, double julian_day) const;

    bool load(const std::string& path, const DataSource* data_source = nullptr);
    bool load_from_string(const std::string& content);
    bool load_from_json(const nlohmann::json& j);
    bool load_embedded_default();

    const std::vector<double>& jds() const { return jds_; }
    const std::vector<Vector3>& sun_vectors() const { return sun_; }
    const std::vector<double>& sun_distances() const { return sun_distance_; }
    const std::vector<Vector3>& moon_vectors() const { return moon_; }
    const std::vector<double>& moon_distances() const { return moon_distance_; }

    static Vector3 moon_to_sun_direction(
        const Vector3& sun_equatorial,
        double sun_distance_au,
        const Vector3& moon_equatorial,
        double moon_distance_au
    );

    static double moon_illuminated_fraction(
        const Vector3& sun_equatorial,
        double sun_distance_au,
        const Vector3& moon_equatorial,
        double moon_distance_au
    );

private:
    std::vector<double> jds_;
    std::vector<Vector3> sun_;
    std::vector<double> sun_distance_;
    std::vector<Vector3> moon_;
    std::vector<double> moon_distance_;
    std::string problem_{"not_loaded"};

    size_t upper_bound_jd(double julian_day) const;
    CelestialSample sample_at(const std::string& body, size_t index, bool interpolated) const;
};

} // namespace thru

#include "thru/celestial_ephemeris.h"
#include <sstream>
#include <cstdlib>
#include <cctype>

namespace thru {

namespace {

static const char* const EMBEDDED_EPHEMERIS_TSV =
    "# JPL Horizons geocentric apparent-of-date coordinates\n"
    "# jd\tsun_ra_deg\tsun_dec_deg\tsun_distance_au\tmoon_ra_deg\tmoon_dec_deg\tmoon_distance_au\n"
    "2461100.5000\t341.9132\t-7.6655\t0.990715\t132.2927\t20.5161\t0.002504\n"
    "2461122.8750\t2.5150\t1.0900\t0.996680\t57.0548\t25.2934\t0.002455\n"
    "2461145.2500\t22.9700\t9.6027\t1.003064\t348.9898\t-3.7324\t0.002517\n"
    "2461167.6250\t44.1151\t16.7926\t1.008917\t287.6327\t-26.3549\t0.002697\n"
    "2461190.0000\t66.3836\t21.6637\t1.013485\t223.7575\t-21.6910\t0.002700\n"
    "2461212.3750\t89.5055\t23.4372\t1.016165\t167.5685\t3.8868\t0.002556\n"
    "2461234.7500\t112.5802\t21.8160\t1.016535\t95.1272\t27.6309\t0.002400\n"
    "2461257.1250\t134.7203\t17.1212\t1.014509\t20.0851\t13.0367\t0.002533\n"
    "2461279.5000\t155.6682\t10.1275\t1.010426\t322.7097\t-15.6701\t0.002638\n"
    "2461301.8750\t175.8492\t1.7972\t1.004879\t258.8720\t-27.9571\t0.002700\n"
    "2461324.2500\t196.0876\t-6.8504\t0.998584\t195.5882\t-10.8686\t0.002594\n"
    "2461346.6250\t217.2993\t-14.7193\t0.992401\t136.0277\t18.0072\t0.002497\n"
    "2461369.0000\t240.1311\t-20.6028\t0.987307\t57.2207\t25.1233\t0.002413\n"
    "2461391.3750\t264.4639\t-23.3399\t0.984155\t350.4995\t-1.4352\t0.002620\n"
    "2461413.7500\t289.1924\t-22.2654\t0.983388\t294.2363\t-24.1079\t0.002716\n"
    "2461437.5000\t314.3407\t-17.2263\t0.985274\t248.0115\t-26.9284\t0.002694\n";

std::string trim(const std::string& s) {
    size_t start = 0;
    while (start < s.size() && (std::isspace(static_cast<unsigned char>(s[start])) != 0)) {
        ++start;
    }
    size_t end = s.size();
    while (end > start && (std::isspace(static_cast<unsigned char>(s[end - 1])) != 0)) {
        --end;
    }
    return s.substr(start, end - start);
}

std::vector<std::string> split(const std::string& s, char delim) {
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream token_stream(s);
    while (std::getline(token_stream, token, delim)) {
        tokens.push_back(token);
    }
    if (!s.empty() && s.back() == delim) {
        tokens.emplace_back("");
    }
    return tokens;
}

bool parse_double(const std::string& s, double& out) {
    if (s.empty()) {
        return false;
    }
    char* end = nullptr;
    out = std::strtod(s.c_str(), &end);
    return end != s.c_str() && *end == '\0';
}

} // namespace

CelestialEphemeris CelestialEphemeris::load_default(const DataSource* data_source) {
    CelestialEphemeris result;
    if (data_source && data_source->exists(DEFAULT_PATH)) {
        result.load(DEFAULT_PATH, data_source);
        return result;
    }
    FileDataSource file_ds;
    if (file_ds.exists(DEFAULT_PATH)) {
        result.load(DEFAULT_PATH, &file_ds);
        return result;
    }
    const std::string res_prefix = std::string("res://") + DEFAULT_PATH;
    if (file_ds.exists(res_prefix)) {
        result.load(res_prefix, &file_ds);
        return result;
    }
    result.load_embedded_default();
    return result;
}

CelestialEphemeris CelestialEphemeris::load_path(const std::string& path, const DataSource* data_source) {
    CelestialEphemeris result;
    result.load(path, data_source);
    return result;
}

CelestialEphemeris CelestialEphemeris::load_string(const std::string& content) {
    CelestialEphemeris result;
    result.load_from_string(content);
    return result;
}

CelestialEphemeris CelestialEphemeris::load_json(const nlohmann::json& j) {
    CelestialEphemeris result;
    result.load_from_json(j);
    return result;
}

bool CelestialEphemeris::load(const std::string& path, const DataSource* data_source) {
    jds_.clear();
    sun_.clear();
    sun_distance_.clear();
    moon_.clear();
    moon_distance_.clear();

    if (data_source != nullptr) {
        if (!data_source->exists(path)) {
            problem_ = "missing_ephemeris";
            return false;
        }
        std::string content = data_source->read_string(path);
        return load_from_string(content);
    }

    FileDataSource file_ds;
    std::string target_path = path;
    if (!file_ds.exists(target_path)) {
        if (target_path.rfind("res://", 0) == 0) {
            target_path = target_path.substr(6);
        }
        if (!file_ds.exists(target_path)) {
            problem_ = "missing_ephemeris";
            return false;
        }
    }

    std::string content = file_ds.read_string(target_path);
    return load_from_string(content);
}

bool CelestialEphemeris::load_from_string(const std::string& content) {
    jds_.clear();
    sun_.clear();
    sun_distance_.clear();
    moon_.clear();
    moon_distance_.clear();

    const std::string trimmed_content = trim(content);
    if (!trimmed_content.empty() && (trimmed_content.front() == '[' || trimmed_content.front() == '{')) {
        try {
            nlohmann::json j = nlohmann::json::parse(trimmed_content);
            return load_from_json(j);
        } catch (...) {
            problem_ = "malformed_ephemeris";
            return false;
        }
    }

    std::istringstream stream(content);
    std::string line;
    while (std::getline(stream, line)) {
        const std::string trimmed = trim(line);
        if (trimmed.empty() || trimmed[0] == '#') {
            continue;
        }
        const std::vector<std::string> fields = split(trimmed, '\t');
        if (fields.size() != 7) {
            problem_ = "malformed_ephemeris";
            jds_.clear();
            sun_.clear();
            sun_distance_.clear();
            moon_.clear();
            moon_distance_.clear();
            return false;
        }
        double values[7];
        for (size_t i = 0; i < 7; ++i) {
            if (!parse_double(fields[i], values[i])) {
                problem_ = "malformed_ephemeris";
                jds_.clear();
                sun_.clear();
                sun_distance_.clear();
                moon_.clear();
                moon_distance_.clear();
                return false;
            }
        }
        const double jd = values[0];
        if (!jds_.empty() && jd <= jds_.back()) {
            problem_ = "unordered_ephemeris";
            jds_.clear();
            sun_.clear();
            sun_distance_.clear();
            moon_.clear();
            moon_distance_.clear();
            return false;
        }
        jds_.push_back(jd);
        sun_.push_back(CelestialMath::equatorial_vector(values[1], values[2]));
        sun_distance_.push_back(values[3]);
        moon_.push_back(CelestialMath::equatorial_vector(values[4], values[5]));
        moon_distance_.push_back(values[6]);
    }

    problem_ = (jds_.size() >= 2) ? "" : "empty_ephemeris";
    return is_valid();
}

bool CelestialEphemeris::load_from_json(const nlohmann::json& j) {
    jds_.clear();
    sun_.clear();
    sun_distance_.clear();
    moon_.clear();
    moon_distance_.clear();

    if (!j.is_array()) {
        problem_ = "malformed_ephemeris";
        return false;
    }

    for (const auto& item : j) {
        double jd = 0.0;
        double sun_ra = 0.0;
        double sun_dec = 0.0;
        double sun_dist = 0.0;
        double moon_ra = 0.0;
        double moon_dec = 0.0;
        double moon_dist = 0.0;

        if (item.is_array() && item.size() == 7) {
            if (!item[0].is_number() || !item[1].is_number() || !item[2].is_number() ||
                !item[3].is_number() || !item[4].is_number() || !item[5].is_number() ||
                !item[6].is_number()) {
                problem_ = "malformed_ephemeris";
                jds_.clear();
                sun_.clear();
                sun_distance_.clear();
                moon_.clear();
                moon_distance_.clear();
                return false;
            }
            jd = item[0].get<double>();
            sun_ra = item[1].get<double>();
            sun_dec = item[2].get<double>();
            sun_dist = item[3].get<double>();
            moon_ra = item[4].get<double>();
            moon_dec = item[5].get<double>();
            moon_dist = item[6].get<double>();
        } else if (item.is_object()) {
            if (!item.contains("jd") || !item.contains("sun_ra") || !item.contains("sun_dec") ||
                !item.contains("sun_dist") || !item.contains("moon_ra") || !item.contains("moon_dec") ||
                !item.contains("moon_dist")) {
                problem_ = "malformed_ephemeris";
                jds_.clear();
                sun_.clear();
                sun_distance_.clear();
                moon_.clear();
                moon_distance_.clear();
                return false;
            }
            jd = item["jd"].get<double>();
            sun_ra = item["sun_ra"].get<double>();
            sun_dec = item["sun_dec"].get<double>();
            sun_dist = item["sun_dist"].get<double>();
            moon_ra = item["moon_ra"].get<double>();
            moon_dec = item["moon_dec"].get<double>();
            moon_dist = item["moon_dist"].get<double>();
        } else {
            problem_ = "malformed_ephemeris";
            jds_.clear();
            sun_.clear();
            sun_distance_.clear();
            moon_.clear();
            moon_distance_.clear();
            return false;
        }

        if (!jds_.empty() && jd <= jds_.back()) {
            problem_ = "unordered_ephemeris";
            jds_.clear();
            sun_.clear();
            sun_distance_.clear();
            moon_.clear();
            moon_distance_.clear();
            return false;
        }
        jds_.push_back(jd);
        sun_.push_back(CelestialMath::equatorial_vector(sun_ra, sun_dec));
        sun_distance_.push_back(sun_dist);
        moon_.push_back(CelestialMath::equatorial_vector(moon_ra, moon_dec));
        moon_distance_.push_back(moon_dist);
    }

    problem_ = (jds_.size() >= 2) ? "" : "empty_ephemeris";
    return is_valid();
}

bool CelestialEphemeris::load_embedded_default() {
    return load_from_string(EMBEDDED_EPHEMERIS_TSV);
}

size_t CelestialEphemeris::upper_bound_jd(double julian_day) const {
    const auto it = std::upper_bound(jds_.begin(), jds_.end(), julian_day);
    return static_cast<size_t>(it - jds_.begin());
}

CelestialSample CelestialEphemeris::sample_at(const std::string& body, size_t index, bool interpolated) const {
    const auto& vectors = (body == "sun") ? sun_ : moon_;
    const auto& distances = (body == "sun") ? sun_distance_ : moon_distance_;
    CelestialSample res;
    res.equatorial = vectors[index];
    res.distance_au = distances[index];
    res.interpolated = interpolated;
    res.valid = true;
    return res;
}

CelestialSample CelestialEphemeris::sample(const std::string& body, double julian_day) const {
    if (!is_valid() || (body != "sun" && body != "moon")) {
        return CelestialSample{};
    }
    const size_t n = jds_.size();
    if (n == 0) {
        return CelestialSample{};
    }

    const size_t upper_raw = upper_bound_jd(julian_day);
    const size_t lower = (upper_raw == 0) ? 0 : upper_raw - 1;
    const size_t upper = std::min(n - 1, upper_raw);

    if (lower == upper) {
        return sample_at(body, lower, false);
    }

    const double span = jds_[upper] - jds_[lower];
    const double weight = (span > 0.0) ? std::clamp((julian_day - jds_[lower]) / span, 0.0, 1.0) : 0.0;
    const auto& vectors = (body == "sun") ? sun_ : moon_;
    const auto& distances = (body == "sun") ? sun_distance_ : moon_distance_;

    CelestialSample result;
    result.equatorial = vectors[lower].slerp(vectors[upper], weight).normalized();
    result.distance_au = distances[lower] + (distances[upper] - distances[lower]) * weight;
    result.interpolated = true;
    result.valid = true;
    return result;
}

Vector3 CelestialEphemeris::moon_to_sun_direction(
    const Vector3& sun_equatorial,
    double sun_distance_au,
    const Vector3& moon_equatorial,
    double moon_distance_au
) {
    return (sun_equatorial * sun_distance_au - moon_equatorial * moon_distance_au).normalized();
}

double CelestialEphemeris::moon_illuminated_fraction(
    const Vector3& sun_equatorial,
    double sun_distance_au,
    const Vector3& moon_equatorial,
    double moon_distance_au
) {
    const Vector3 m2s = moon_to_sun_direction(sun_equatorial, sun_distance_au, moon_equatorial, moon_distance_au);
    return std::clamp((1.0 + m2s.dot(-moon_equatorial.normalized())) * 0.5, 0.0, 1.0);
}

} // namespace thru

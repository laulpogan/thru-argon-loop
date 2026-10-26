#include <doctest/doctest.h>
#include "thru/celestial_math.h"
#include "thru/celestial_ephemeris.h"
#include "thru/data_source.h"

#include <cmath>

TEST_CASE("Vector3 and Basis basic operations") {
    // Basic vector math foundation
    thru::Vector3 v1(1.0, 2.0, 3.0);
    thru::Vector3 v2(4.0, 5.0, 6.0);

    CHECK((v1 + v2) == thru::Vector3(5.0, 7.0, 9.0));
    CHECK((v2 - v1) == thru::Vector3(3.0, 3.0, 3.0));
    CHECK((-v1) == thru::Vector3(-1.0, -2.0, -3.0));
    CHECK((v1 * 2.0) == thru::Vector3(2.0, 4.0, 6.0));
    CHECK((2.0 * v1) == thru::Vector3(2.0, 4.0, 6.0));
    CHECK((v1 / 2.0) == thru::Vector3(0.5, 1.0, 1.5));
    CHECK(v1.dot(v2) == doctest::Approx(32.0));

    thru::Vector3 cross = thru::Vector3::right().cross(thru::Vector3::up());
    CHECK(cross.x == doctest::Approx(0.0));
    CHECK(cross.y == doctest::Approx(0.0));
    CHECK(cross.z == doctest::Approx(1.0));

    // Slerp edge cases
    thru::Vector3 north(0.0, 0.0, -1.0);
    thru::Vector3 east(1.0, 0.0, 0.0);
    thru::Vector3 mid = north.slerp(east, 0.5);
    CHECK(mid.x == doctest::Approx(std::sqrt(0.5)));
    CHECK(mid.z == doctest::Approx(-std::sqrt(0.5)));

    // Basis operations
    thru::Basis identity;
    thru::Vector3 transformed = identity * thru::Vector3(3.0, 4.0, 5.0);
    CHECK(transformed == thru::Vector3(3.0, 4.0, 5.0));
}

TEST_CASE("CelestialMath::equatorial_vector cardinal transforms") {
    // GDScript reference: godot/scripts/celestial_math.gd:9-14
    // static func equatorial_vector(ra_degrees: float, dec_degrees: float) -> Vector3:
    // var ra: float = deg_to_rad(ra_degrees)
    // var dec: float = deg_to_rad(dec_degrees)
    // var cos_dec: float = cos(dec)
    // return Vector3(cos_dec * cos(ra), cos_dec * sin(ra), sin(dec)).normalized()

    // (RA=0, Dec=0) -> Vernon Equinox (+X axis)
    const thru::Vector3 v_eq0 = thru::CelestialMath::equatorial_vector(0.0, 0.0);
    CHECK(v_eq0.x == doctest::Approx(1.0));
    CHECK(std::abs(v_eq0.y) < 1e-12);
    CHECK(std::abs(v_eq0.z) < 1e-12);

    // (RA=90, Dec=0) -> (+Y axis)
    const thru::Vector3 v_eq90 = thru::CelestialMath::equatorial_vector(90.0, 0.0);
    CHECK(std::abs(v_eq90.x) < 1e-12);
    CHECK(v_eq90.y == doctest::Approx(1.0));
    CHECK(std::abs(v_eq90.z) < 1e-12);

    // (RA=180, Dec=0) -> (-X axis)
    const thru::Vector3 v_eq180 = thru::CelestialMath::equatorial_vector(180.0, 0.0);
    CHECK(v_eq180.x == doctest::Approx(-1.0));
    CHECK(std::abs(v_eq180.y) < 1e-12);
    CHECK(std::abs(v_eq180.z) < 1e-12);

    // (RA=0, Dec=90) -> North Celestial Pole (+Z axis)
    const thru::Vector3 v_ncp = thru::CelestialMath::equatorial_vector(0.0, 90.0);
    CHECK(std::abs(v_ncp.x) < 1e-12);
    CHECK(std::abs(v_ncp.y) < 1e-12);
    CHECK(v_ncp.z == doctest::Approx(1.0));

    // (RA=0, Dec=-90) -> South Celestial Pole (-Z axis)
    const thru::Vector3 v_scp = thru::CelestialMath::equatorial_vector(0.0, -90.0);
    CHECK(std::abs(v_scp.x) < 1e-12);
    CHECK(std::abs(v_scp.y) < 1e-12);
    CHECK(v_scp.z == doctest::Approx(-1.0));

    // Verify unit length
    const thru::Vector3 v_arb = thru::CelestialMath::equatorial_vector(123.456, -45.678);
    CHECK(v_arb.length() == doctest::Approx(1.0));
}

TEST_CASE("CelestialMath::apparent_sidereal_degrees USNO algorithm") {
    // GDScript reference: godot/scripts/celestial_math.gd:47-66
    // static func apparent_sidereal_degrees(julian_day: float) -> float:
    // Test at J2000.0 epoch: JD 2451545.0 (2000-01-01 12:00 TT)
    const double sidereal_j2000 = thru::CelestialMath::apparent_sidereal_degrees(thru::CelestialMath::J2000);
    // Calculated from GDScript algorithm: 280.4571469189 degrees
    CHECK(sidereal_j2000 == doctest::Approx(280.457146918907).epsilon(1e-6));

    // Test at fixed campaign date: 2026-04-15 noon PDT (JD 2461146.2916666665)
    // (Used across trail calendar and night dark tests)
    constexpr double april_noon_jd = 2461146.2916666665;
    const double sidereal_april = thru::CelestialMath::apparent_sidereal_degrees(april_noon_jd);
    // Calculated from GDScript algorithm: 128.94997037258 degrees
    CHECK(sidereal_april == doctest::Approx(128.94997037258).epsilon(1e-6));

    // Apparent sidereal degrees must strictly be in [0, 360)
    CHECK(sidereal_j2000 >= 0.0);
    CHECK(sidereal_j2000 < 360.0);
    CHECK(sidereal_april >= 0.0);
    CHECK(sidereal_april < 360.0);
}

TEST_CASE("CelestialMath::precession_basis IAU 1976 precession") {
    // GDScript reference: godot/scripts/celestial_math.gd:37-44, 97-113
    // static func precession_basis(julian_day: float) -> Basis:
    // At J2000 epoch, precession angles (zeta, zed, theta) are exactly 0
    const thru::Basis p_j2000 = thru::CelestialMath::precession_basis(thru::CelestialMath::J2000);
    CHECK(p_j2000.x.x == doctest::Approx(1.0));
    CHECK(p_j2000.x.y == doctest::Approx(0.0).epsilon(1e-12));
    CHECK(p_j2000.x.z == doctest::Approx(0.0).epsilon(1e-12));

    CHECK(p_j2000.y.x == doctest::Approx(0.0).epsilon(1e-12));
    CHECK(p_j2000.y.y == doctest::Approx(1.0));
    CHECK(p_j2000.y.z == doctest::Approx(0.0).epsilon(1e-12));

    CHECK(p_j2000.z.x == doctest::Approx(0.0).epsilon(1e-12));
    CHECK(p_j2000.z.y == doctest::Approx(0.0).epsilon(1e-12));
    CHECK(p_j2000.z.z == doctest::Approx(1.0));

    // Precession basis columns must remain orthonormal
    constexpr double jd_2026 = 2461146.2916666665;
    const thru::Basis p_2026 = thru::CelestialMath::precession_basis(jd_2026);
    CHECK(p_2026.x.length() == doctest::Approx(1.0));
    CHECK(p_2026.y.length() == doctest::Approx(1.0));
    CHECK(p_2026.z.length() == doctest::Approx(1.0));
    CHECK(std::abs(p_2026.x.dot(p_2026.y)) < 1e-10);
    CHECK(std::abs(p_2026.x.dot(p_2026.z)) < 1e-10);
    CHECK(std::abs(p_2026.y.dot(p_2026.z)) < 1e-10);
}

TEST_CASE("CelestialMath::horizon_basis and horizontal_direction topocentric geometry") {
    // GDScript reference: godot/scripts/celestial_math.gd:17-19, 25-35
    // static func horizontal_direction(equatorial: Vector3, julian_day: float, latitude: float, longitude: float) -> Vector3:
    // static func horizon_basis(julian_day: float, latitude: float, longitude: float) -> Basis:
    // At North Pole (lat = 90.0), North Celestial Pole (+Z equatorial) must point straight to Zenith (+Y horizontal)
    const thru::Vector3 ncp = thru::CelestialMath::equatorial_vector(0.0, 90.0);
    constexpr double test_jd = 2461146.2916666665;
    const thru::Vector3 dir_np = thru::CelestialMath::horizontal_direction(ncp, test_jd, 90.0, 0.0);
    CHECK(dir_np.x == doctest::Approx(0.0).epsilon(1e-12));
    CHECK(dir_np.y == doctest::Approx(1.0));
    CHECK(dir_np.z == doctest::Approx(0.0).epsilon(1e-12));
    CHECK(thru::CelestialMath::altitude(dir_np) == doctest::Approx(90.0));

    // At Equator (lat = 0.0), North Celestial Pole must sit on the northern horizon (altitude = 0, North is -Z in Godot)
    const thru::Vector3 dir_eq = thru::CelestialMath::horizontal_direction(ncp, test_jd, 0.0, 0.0);
    CHECK(dir_eq.x == doctest::Approx(0.0).epsilon(1e-12));
    CHECK(dir_eq.y == doctest::Approx(0.0).epsilon(1e-12));
    CHECK(dir_eq.z == doctest::Approx(-1.0));
    CHECK(thru::CelestialMath::altitude(dir_eq) == doctest::Approx(0.0));
    CHECK(thru::CelestialMath::azimuth(dir_eq) == doctest::Approx(0.0));

    // J2000 horizontal basis combines horizon and precession
    const thru::Basis j2000_basis = thru::CelestialMath::j2000_horizontal_basis(test_jd, 36.5, -118.0);
    CHECK(j2000_basis.x.length() == doctest::Approx(1.0));
    CHECK(j2000_basis.y.length() == doctest::Approx(1.0));
    CHECK(j2000_basis.z.length() == doctest::Approx(1.0));
}

TEST_CASE("CelestialMath::topocentric_equatorial parallax correction") {
    // GDScript reference: godot/scripts/celestial_math.gd:69-95
    // static func topocentric_equatorial(geocentric: Vector3, distance_au: float, julian_day: float, latitude: float, longitude: float, elevation_metres: float = 0.0) -> Vector3:
    const thru::Vector3 geo = thru::CelestialMath::equatorial_vector(180.0, 0.0);
    constexpr double jd = 2461146.2916666665;
    constexpr double lat = 36.5785;  // Mt Whitney
    constexpr double lon = -118.2923;
    constexpr double elev = 4421.0;

    // Body too close (inside Earth equatorial radius) -> returns geocentric normalized
    const thru::Vector3 inside_earth = thru::CelestialMath::topocentric_equatorial(
        geo, thru::CelestialMath::EARTH_EQUATORIAL_RADIUS_AU * 0.5, jd, lat, lon, elev);
    CHECK(inside_earth.x == doctest::Approx(geo.x));
    CHECK(inside_earth.y == doctest::Approx(geo.y));
    CHECK(inside_earth.z == doctest::Approx(geo.z));

    // Moon at ~0.00257 AU (~384,400 km) -> topocentric parallax shift
    // GDScript formulas yield RA = 180.13959986 deg, Dec = -0.55638612 deg
    const thru::Vector3 moon_topo = thru::CelestialMath::topocentric_equatorial(
        geo, 0.00257, jd, lat, lon, elev);
    const double expected_ra = 180.13959986248489;
    const double expected_dec = -0.5563861240854447;
    const thru::Vector3 expected_topo = thru::CelestialMath::equatorial_vector(expected_ra, expected_dec);
    CHECK(moon_topo.x == doctest::Approx(expected_topo.x).epsilon(1e-6));
    CHECK(moon_topo.y == doctest::Approx(expected_topo.y).epsilon(1e-6));
    CHECK(moon_topo.z == doctest::Approx(expected_topo.z).epsilon(1e-6));

    // Distant sun (~1.0 AU) -> negligible parallax (< 9 arcseconds / 0.0025 deg)
    const thru::Vector3 sun_topo = thru::CelestialMath::topocentric_equatorial(
        geo, 1.0, jd, lat, lon, elev);
    CHECK(sun_topo.dot(geo) > 0.9999999);
}

TEST_CASE("CelestialEphemeris loading, problems, and error handling") {
    // GDScript reference: godot/scripts/celestial_ephemeris.gd:47-81
    // Uninitialized ephemeris
    thru::CelestialEphemeris uninit;
    CHECK_FALSE(uninit.is_valid());
    CHECK(uninit.problem() == "not_loaded");
    CHECK_FALSE(uninit.sample("sun", 2461151.0).valid);

    // Missing file fails closed (matching godot/tests/atmosphere_check.gd:92-94)
    // var missing_ephemeris := CelestialEphemeris.load_path("res://data/celestial/not-present.tsv")
    // _check(not missing_ephemeris.is_valid() and missing_ephemeris.sample("sun", 2461151.0).is_empty())
    thru::CelestialEphemeris missing = thru::CelestialEphemeris::load_path("data/celestial/not-present.tsv");
    CHECK_FALSE(missing.is_valid());
    CHECK(missing.problem() == "missing_ephemeris");
    CHECK_FALSE(missing.sample("sun", 2461151.0).valid);

    // Malformed TSV data rejected (matching godot/tests/atmosphere_check.gd:98-100)
    // malformed_file.store_string("not\tan\tephemeris\n")
    // _check(not malformed_ephemeris.is_valid() and malformed_ephemeris.problem() == "malformed_ephemeris")
    thru::CelestialEphemeris malformed = thru::CelestialEphemeris::load_string("not\tan\tephemeris\n");
    CHECK_FALSE(malformed.is_valid());
    CHECK(malformed.problem() == "malformed_ephemeris");

    // Malformed float field
    thru::CelestialEphemeris bad_float = thru::CelestialEphemeris::load_string(
        "2461100.0\t10.0\tbad\t1.0\t20.0\t-3.0\t0.0025\n"
        "2461101.0\t11.0\t6.0\t1.0\t32.0\t-4.0\t0.0025\n");
    CHECK_FALSE(bad_float.is_valid());
    CHECK(bad_float.problem() == "malformed_ephemeris");

    // Unordered Julian Day records
    thru::CelestialEphemeris unordered = thru::CelestialEphemeris::load_string(
        "2461101.0\t10.0\t5.0\t1.0\t20.0\t-3.0\t0.0025\n"
        "2461100.0\t11.0\t6.0\t1.0\t32.0\t-4.0\t0.0025\n");
    CHECK_FALSE(unordered.is_valid());
    CHECK(unordered.problem() == "unordered_ephemeris");

    // Equal successive Julian Days (strictly ascending required: jd <= _jds[-1])
    thru::CelestialEphemeris duplicate_jd = thru::CelestialEphemeris::load_string(
        "2461100.0\t10.0\t5.0\t1.0\t20.0\t-3.0\t0.0025\n"
        "2461100.0\t11.0\t6.0\t1.0\t32.0\t-4.0\t0.0025\n");
    CHECK_FALSE(duplicate_jd.is_valid());
    CHECK(duplicate_jd.problem() == "unordered_ephemeris");

    // Empty / single-line file (requires >= 2 rows for interpolation)
    thru::CelestialEphemeris single_line = thru::CelestialEphemeris::load_string(
        "2461100.0\t10.0\t5.0\t1.0\t20.0\t-3.0\t0.0025\n");
    CHECK_FALSE(single_line.is_valid());
    CHECK(single_line.problem() == "empty_ephemeris");

    thru::CelestialEphemeris empty_tsv = thru::CelestialEphemeris::load_string("# only comments\n");
    CHECK_FALSE(empty_tsv.is_valid());
    CHECK(empty_tsv.problem() == "empty_ephemeris");
}

TEST_CASE("CelestialEphemeris embedded default and sampling") {
    // GDScript reference: godot/scripts/celestial_ephemeris.gd:15-17, 28-44
    // static func load_default() -> CelestialEphemeris:
    thru::CelestialEphemeris ephem = thru::CelestialEphemeris::load_default();
    CHECK(ephem.is_valid());
    CHECK(ephem.problem().empty());
    CHECK(ephem.size() == 16);

    // Knot dates span March 1, 2026 (JD 2461100.5) to February 1, 2027 (JD 2461437.5)
    CHECK(ephem.jds().front() == doctest::Approx(2461100.5));
    CHECK(ephem.jds().back() == doctest::Approx(2461437.5));

    // Sample invalid body
    CHECK_FALSE(ephem.sample("mars", 2461150.0).valid);

    // Clamping before first sample: lower == upper == 0, interpolated = false
    auto sample_early = ephem.sample("sun", 2461000.0);
    CHECK(sample_early.valid);
    CHECK_FALSE(sample_early.interpolated);
    CHECK(sample_early.distance_au == doctest::Approx(ephem.sun_distances().front()));
    CHECK(sample_early.equatorial == ephem.sun_vectors().front());

    // Clamping after last sample: lower == upper == size - 1, interpolated = false
    auto sample_late = ephem.sample("moon", 2461500.0);
    CHECK(sample_late.valid);
    CHECK_FALSE(sample_late.interpolated);
    CHECK(sample_late.distance_au == doctest::Approx(ephem.moon_distances().back()));
    CHECK(sample_late.equatorial == ephem.moon_vectors().back());

    // Mid-interval interpolation: interpolated = true
    // Midpoint between knot 0 (JD 2461100.5) and knot 1 (JD 2461122.875)
    constexpr double jd_mid = 0.5 * (2461100.5 + 2461122.875);
    auto sample_mid = ephem.sample("sun", jd_mid);
    CHECK(sample_mid.valid);
    CHECK(sample_mid.interpolated);
    // Linear lerp of distances
    const double expected_dist = 0.5 * (ephem.sun_distances()[0] + ephem.sun_distances()[1]);
    CHECK(sample_mid.distance_au == doctest::Approx(expected_dist));
    // Slerp of unit vectors
    const thru::Vector3 expected_vec = ephem.sun_vectors()[0].slerp(ephem.sun_vectors()[1], 0.5).normalized();
    CHECK(sample_mid.equatorial.x == doctest::Approx(expected_vec.x).epsilon(1e-6));
    CHECK(sample_mid.equatorial.y == doctest::Approx(expected_vec.y).epsilon(1e-6));
    CHECK(sample_mid.equatorial.z == doctest::Approx(expected_vec.z).epsilon(1e-6));
}

TEST_CASE("CelestialEphemeris DataSource integration (TSV and JSON)") {
    // Interface testing with MemoryDataSource
    thru::MemoryDataSource mem_ds;

    // Put TSV data into memory source
    const std::string tsv_data =
        "# jd\tsun_ra_deg\tsun_dec_deg\tsun_distance_au\tmoon_ra_deg\tmoon_dec_deg\tmoon_distance_au\n"
        "2461100.0\t10.0\t5.0\t1.001\t20.0\t-3.0\t0.0025\n"
        "2461110.0\t20.0\t8.0\t1.002\t140.0\t15.0\t0.0026\n";
    mem_ds.put_string("data/celestial/test.tsv", tsv_data);

    thru::CelestialEphemeris tsv_ephem;
    CHECK(tsv_ephem.load("data/celestial/test.tsv", &mem_ds));
    CHECK(tsv_ephem.is_valid());
    CHECK(tsv_ephem.size() == 2);

    auto sun_sample = tsv_ephem.sample("sun", 2461105.0);
    CHECK(sun_sample.valid);
    CHECK(sun_sample.interpolated);
    CHECK(sun_sample.distance_au == doctest::Approx(1.0015));

    // Put JSON array format into memory source
    nlohmann::json json_data = nlohmann::json::array({
        {
            {"jd", 2461100.0},
            {"sun_ra", 10.0},
            {"sun_dec", 5.0},
            {"sun_dist", 1.001},
            {"moon_ra", 20.0},
            {"moon_dec", -3.0},
            {"moon_dist", 0.0025}
        },
        {
            {"jd", 2461110.0},
            {"sun_ra", 20.0},
            {"sun_dec", 8.0},
            {"sun_dist", 1.002},
            {"moon_ra", 140.0},
            {"moon_dec", 15.0},
            {"moon_dist", 0.0026}
        }
    });
    mem_ds.put_json("data/celestial/test.json", json_data);

    thru::CelestialEphemeris json_ephem;
    CHECK(json_ephem.load("data/celestial/test.json", &mem_ds));
    CHECK(json_ephem.is_valid());
    CHECK(json_ephem.size() == 2);

    auto moon_sample = json_ephem.sample("moon", 2461105.0);
    CHECK(moon_sample.valid);
    CHECK(moon_sample.interpolated);
    CHECK(moon_sample.distance_au == doctest::Approx(0.00255));
}

TEST_CASE("CelestialEphemeris Moon illumination and phase geometry") {
    // GDScript reference: godot/scripts/geo_atmosphere.gd:511-516
    // var moon_to_sun: Vector3 = (sun_equatorial * sun_distance_au - moon_equatorial * moon_distance_au).normalized()
    // moon_illuminated_fraction = clampf((1.0 + moon_to_sun.dot(-moon_equatorial)) * 0.5, 0.0, 1.0)
    // godot/tests/night_dark/check.gd:178-183

    // Full moon: Sun and Moon on opposite sides of Earth
    const thru::Vector3 sun_full = thru::CelestialMath::equatorial_vector(0.0, 0.0);
    const thru::Vector3 moon_full = thru::CelestialMath::equatorial_vector(180.0, 0.0);
    const double fraction_full = thru::CelestialEphemeris::moon_illuminated_fraction(
        sun_full, 1.0, moon_full, 0.00257);
    CHECK(fraction_full > 0.999);

    // New moon: Sun and Moon on same side of Earth
    const thru::Vector3 sun_new = thru::CelestialMath::equatorial_vector(45.0, 10.0);
    const thru::Vector3 moon_new = thru::CelestialMath::equatorial_vector(45.0, 10.0);
    const double fraction_new = thru::CelestialEphemeris::moon_illuminated_fraction(
        sun_new, 1.0, moon_new, 0.00257);
    CHECK(fraction_new < 0.001);

    // First quarter: Sun and Moon at 90 degrees separation
    const thru::Vector3 sun_quarter = thru::CelestialMath::equatorial_vector(0.0, 0.0);
    const thru::Vector3 moon_quarter = thru::CelestialMath::equatorial_vector(90.0, 0.0);
    const double fraction_quarter = thru::CelestialEphemeris::moon_illuminated_fraction(
        sun_quarter, 1.0, moon_quarter, 0.00257);
    CHECK(fraction_quarter == doctest::Approx(0.5).epsilon(0.01));
}

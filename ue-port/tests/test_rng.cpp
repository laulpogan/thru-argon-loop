#include <doctest/doctest.h>
#include "thru/rng.h"
#include <vector>

TEST_CASE("thru::Rng deterministic sequence reproducibility") {
    // GDScript reference: godot/scripts/hiker_cohort.gd:507
    // Deterministic random numbers seeded by an integer must yield identical sequences on every peer.
    thru::Rng rng1(1998ULL);
    thru::Rng rng2(1998ULL);

    for (int i = 0; i < 100; ++i) {
        // Both RNG instances initialized with identical seeds must produce identical u64 outputs
        CHECK(rng1.next_u64() == rng2.next_u64());
    }

    // Re-seeding with the same seed resets the sequence
    rng1.seed(1998ULL);
    rng2.seed(1998ULL);
    CHECK(rng1.next_u64() == rng2.next_u64());
}

TEST_CASE("thru::Rng bounds and distributions") {
    thru::Rng rng(42ULL);

    for (int i = 0; i < 1000; ++i) {
        // Floating point in [0.0, 1.0)
        double d = rng.next_double();
        CHECK(d >= 0.0);
        CHECK(d < 1.0);

        float f = rng.next_float();
        CHECK(f >= 0.0f);
        CHECK(f < 1.0f);

        // Integer range [min_incl, max_incl]
        // GDScript reference: godot/scripts/hiker_cohort.gd:522 draw.randi_range(min, max)
        int32_t val32 = rng.range_i32(2, 7);
        CHECK(val32 >= 2);
        CHECK(val32 <= 7);

        int64_t val64 = rng.range_i64(-50, 50);
        CHECK(val64 >= -50);
        CHECK(val64 <= 50);

        double range_d = rng.range_double(10.0, 20.0);
        CHECK(range_d >= 10.0);
        CHECK(range_d < 20.0);
    }
}

TEST_CASE("thru::Rng state save and restore") {
    // GDScript reference: godot/scripts/world_event_journal.gd:61 save_state / restore
    thru::Rng rng(12345ULL);
    for (int i = 0; i < 50; ++i) {
        rng.next_u64();
    }

    auto saved_state = rng.get_state();
    std::vector<uint64_t> expected;
    for (int i = 0; i < 50; ++i) {
        expected.push_back(rng.next_u64());
    }

    // Restore saved state
    rng.set_state(saved_state);
    for (int i = 0; i < 50; ++i) {
        CHECK(rng.next_u64() == expected[i]);
    }
}

TEST_CASE("thru::Rng chance probabilities") {
    thru::Rng rng(999ULL);
    // Boundary conditions
    CHECK_FALSE(rng.chance(0.0));
    CHECK_FALSE(rng.chance(-0.5));
    CHECK(rng.chance(1.0));
    CHECK(rng.chance(1.5));
}

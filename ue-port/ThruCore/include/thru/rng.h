#pragma once

#include <cstdint>
#include <array>

namespace thru {

/**
 * Seeded deterministic pseudo-random number generator (xoshiro256** with splitmix64).
 * Ensures identical sequences across co-op peers given the same seed.
 */
class Rng {
public:
    explicit Rng(uint64_t initial_seed = 0x853c49e6748fea9bULL);

    void seed(uint64_t new_seed);

    uint64_t next_u64();
    uint32_t next_u32();

    double next_double(); // [0.0, 1.0)
    float next_float();   // [0.0f, 1.0f)

    int64_t range_i64(int64_t min_incl, int64_t max_incl);
    int32_t range_i32(int32_t min_incl, int32_t max_incl);
    double range_double(double min_val, double max_val);
    float range_float(float min_val, float max_val);

    bool chance(double probability);

    std::array<uint64_t, 4> get_state() const;
    void set_state(const std::array<uint64_t, 4>& state);

private:
    std::array<uint64_t, 4> s_{};
};

} // namespace thru

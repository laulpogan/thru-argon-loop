#include "thru/rng.h"
#include <cmath>

namespace thru {

namespace {

inline uint64_t splitmix64_next(uint64_t& x) {
    uint64_t z = (x += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

inline uint64_t rotl(const uint64_t x, int k) {
    return (x << k) | (x >> (64 - k));
}

} // namespace

Rng::Rng(uint64_t initial_seed) {
    seed(initial_seed);
}

void Rng::seed(uint64_t new_seed) {
    uint64_t sm = new_seed;
    s_[0] = splitmix64_next(sm);
    s_[1] = splitmix64_next(sm);
    s_[2] = splitmix64_next(sm);
    s_[3] = splitmix64_next(sm);
    if ((s_[0] | s_[1] | s_[2] | s_[3]) == 0ULL) {
        s_[0] = 1ULL;
    }
}

uint64_t Rng::next_u64() {
    const uint64_t result = rotl(s_[1] * 5, 7) * 9;
    const uint64_t t = s_[1] << 17;

    s_[2] ^= s_[0];
    s_[3] ^= s_[1];
    s_[1] ^= s_[2];
    s_[0] ^= s_[3];

    s_[2] ^= t;
    s_[3] = rotl(s_[3], 45);

    return result;
}

uint32_t Rng::next_u32() {
    return static_cast<uint32_t>(next_u64() >> 32);
}

double Rng::next_double() {
    // 53 bits of precision into [0.0, 1.0)
    return static_cast<double>(next_u64() >> 11) * (1.0 / 9007199254740992.0);
}

float Rng::next_float() {
    // 24 bits of precision into [0.0f, 1.0f)
    return static_cast<float>(next_u32() >> 8) * (1.0f / 16777216.0f);
}

int64_t Rng::range_i64(int64_t min_incl, int64_t max_incl) {
    if (min_incl >= max_incl) {
        return min_incl;
    }
    const uint64_t span = static_cast<uint64_t>(max_incl - min_incl) + 1ULL;
    return min_incl + static_cast<int64_t>(next_u64() % span);
}

int32_t Rng::range_i32(int32_t min_incl, int32_t max_incl) {
    if (min_incl >= max_incl) {
        return min_incl;
    }
    const uint32_t span = static_cast<uint32_t>(max_incl - min_incl) + 1U;
    return min_incl + static_cast<int32_t>(next_u32() % span);
}

double Rng::range_double(double min_val, double max_val) {
    if (min_val >= max_val) {
        return min_val;
    }
    return min_val + (max_val - min_val) * next_double();
}

float Rng::range_float(float min_val, float max_val) {
    if (min_val >= max_val) {
        return min_val;
    }
    return min_val + (max_val - min_val) * next_float();
}

bool Rng::chance(double probability) {
    if (probability <= 0.0) {
        return false;
    }
    if (probability >= 1.0) {
        return true;
    }
    return next_double() < probability;
}

std::array<uint64_t, 4> Rng::get_state() const {
    return s_;
}

void Rng::set_state(const std::array<uint64_t, 4>& state) {
    s_ = state;
}

} // namespace thru

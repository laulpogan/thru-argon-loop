#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "thru/celestial_ephemeris.h"
#include "ThruCelestialEphemeris.generated.h"

USTRUCT(BlueprintType)
struct THRUGAME_API FThruCelestialSample
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Celestial")
    FVector Equatorial = FVector::ZeroVector;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Celestial")
    double DistanceAu = 0.0;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Celestial")
    bool bInterpolated = false;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Celestial")
    bool bValid = false;

    static FThruCelestialSample FromCore(const thru::CelestialSample& Core)
    {
        FThruCelestialSample Out;
        Out.Equatorial = FVector(Core.equatorial.x, Core.equatorial.y, Core.equatorial.z);
        Out.DistanceAu = Core.distance_au;
        Out.bInterpolated = Core.interpolated;
        Out.bValid = Core.valid;
        return Out;
    }
};

/**
 * Ephemeris table sampler for Sun and Moon topocentric and geocentric calculations.
 */
UCLASS(BlueprintType)
class THRUGAME_API UThruCelestialEphemeris : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Celestial")
    bool LoadDefault();

    UFUNCTION(BlueprintCallable, Category = "Celestial")
    bool LoadPath(const FString& Path);

    UFUNCTION(BlueprintCallable, Category = "Celestial")
    bool LoadString(const FString& Content);

    UFUNCTION(BlueprintPure, Category = "Celestial")
    bool IsValid() const;

    UFUNCTION(BlueprintPure, Category = "Celestial")
    FString GetProblem() const;

    UFUNCTION(BlueprintPure, Category = "Celestial")
    int32 GetSampleCount() const;

    UFUNCTION(BlueprintPure, Category = "Celestial")
    FThruCelestialSample Sample(const FString& Body, double JulianDay) const;

    UFUNCTION(BlueprintPure, Category = "Celestial")
    static FVector MoonToSunDirection(
        const FVector& SunEquatorial,
        double SunDistanceAu,
        const FVector& MoonEquatorial,
        double MoonDistanceAu
    );

    UFUNCTION(BlueprintPure, Category = "Celestial")
    static double MoonIlluminatedFraction(
        const FVector& SunEquatorial,
        double SunDistanceAu,
        const FVector& MoonEquatorial,
        double MoonDistanceAu
    );

    thru::CelestialEphemeris& GetCore() { return CoreEphemeris; }
    const thru::CelestialEphemeris& GetCore() const { return CoreEphemeris; }

private:
    thru::CelestialEphemeris CoreEphemeris;
};

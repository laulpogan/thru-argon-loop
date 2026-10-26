#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "thru/celestial_math.h"
#include "ThruCelestialMathLibrary.generated.h"

USTRUCT(BlueprintType)
struct THRUGAME_API FThruBasis
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Celestial")
    FVector X = FVector(1.0, 0.0, 0.0);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Celestial")
    FVector Y = FVector(0.0, 1.0, 0.0);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Celestial")
    FVector Z = FVector(0.0, 0.0, 1.0);

    static FThruBasis FromCore(const thru::Basis& Core)
    {
        FThruBasis Out;
        Out.X = FVector(Core.x.x, Core.x.y, Core.x.z);
        Out.Y = FVector(Core.y.x, Core.y.y, Core.y.z);
        Out.Z = FVector(Core.z.x, Core.z.y, Core.z.z);
        return Out;
    }

    thru::Basis ToCore() const
    {
        return thru::Basis(
            thru::Vector3(X.X, X.Y, X.Z),
            thru::Vector3(Y.X, Y.Y, Y.Z),
            thru::Vector3(Z.X, Z.Y, Z.Z)
        );
    }
};

/**
 * Blueprint library exposing astronomical coordinate frames, transforms, and apparent sidereal time.
 */
UCLASS()
class THRUGAME_API UThruCelestialMathLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintPure, Category = "Celestial")
    static FVector EquatorialVector(double RaDegrees, double DecDegrees);

    UFUNCTION(BlueprintPure, Category = "Celestial")
    static FVector HorizontalDirection(const FVector& Equatorial, double JulianDay, double Latitude, double Longitude);

    UFUNCTION(BlueprintPure, Category = "Celestial")
    static FThruBasis J2000HorizontalBasis(double JulianDay, double Latitude, double Longitude);

    UFUNCTION(BlueprintPure, Category = "Celestial")
    static FThruBasis HorizonBasis(double JulianDay, double Latitude, double Longitude);

    UFUNCTION(BlueprintPure, Category = "Celestial")
    static FThruBasis PrecessionBasis(double JulianDay);

    UFUNCTION(BlueprintPure, Category = "Celestial")
    static double ApparentSiderealDegrees(double JulianDay);

    UFUNCTION(BlueprintPure, Category = "Celestial")
    static FVector TopocentricEquatorial(
        const FVector& Geocentric,
        double DistanceAu,
        double JulianDay,
        double Latitude,
        double Longitude,
        double ElevationMetres = 0.0
    );

    UFUNCTION(BlueprintPure, Category = "Celestial")
    static double Azimuth(const FVector& Direction);

    UFUNCTION(BlueprintPure, Category = "Celestial")
    static double Altitude(const FVector& Direction);
};

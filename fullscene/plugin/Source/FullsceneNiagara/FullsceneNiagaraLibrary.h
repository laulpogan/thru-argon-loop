#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "FullsceneNiagaraLibrary.generated.h"
class UNiagaraSystem;
class UStaticMesh;
class USkeletalMeshComponent;
UCLASS()
class FULLSCENENIAGARA_API UFullsceneNiagaraLibrary : public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable,Category="Fullscene")
 static UStaticMesh* BakeFauna(USkeletalMeshComponent* Component,const FString& AssetPath);
 UFUNCTION(BlueprintCallable,Category="Fullscene")
 static UNiagaraSystem* MakeAmbient(const FString& AssetPath,const FString& EmitterPath,UStaticMesh* Mesh,int32 Seed,float MeshScale);
};

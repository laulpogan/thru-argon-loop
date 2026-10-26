#include "FullsceneNiagaraLibrary.h"
#include "Modules/ModuleManager.h"
#include "MeshUtilities.h"
#include "Components/SkeletalMeshComponent.h"
#include "NiagaraSystem.h"
#include "NiagaraEmitter.h"
#include "NiagaraEmitterHandle.h"
#include "NiagaraSystemFactoryNew.h"
#include "NiagaraEditorUtilities.h"
#include "NiagaraMeshRendererProperties.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "Misc/PackageName.h"
IMPLEMENT_MODULE(FDefaultModuleImpl,FullsceneNiagara)
UNiagaraSystem* UFullsceneNiagaraLibrary::MakeAmbient(const FString& AssetPath,const FString& EmitterPath,UStaticMesh* Mesh,int32 Seed,float MeshScale) {
 if (!AssetPath.StartsWith(TEXT("/Game/FullsceneVFX/"))) return nullptr;
 if (auto* Existing=LoadObject<UNiagaraSystem>(nullptr,*AssetPath)) return Existing;
 auto* Source=LoadObject<UNiagaraEmitter>(nullptr,*EmitterPath);
 if (!Source) return nullptr;
 UPackage* Package=CreatePackage(*AssetPath);
 auto* System=NewObject<UNiagaraSystem>(Package,*FPackageName::GetLongPackageAssetName(AssetPath),RF_Public|RF_Standalone|RF_Transactional);
 UNiagaraSystemFactoryNew::InitializeSystem(System,true);
 FNiagaraEditorUtilities::AddEmitterToSystem(*System,*Source,Source->GetExposedVersion().VersionGuid,true);
 auto Instance=System->GetEmitterHandles().Last().GetInstance();
 auto* Data=Instance.GetEmitterData();
 Data->bDeterminism=true;Data->RandomSeed=Seed;Data->bLocalSpace=true;
 if (Mesh) {
  auto Renderers=Data->GetRenderers();
  for (auto* Renderer:Renderers) Instance.Emitter->RemoveRenderer(Renderer,Instance.Version);
  auto* Renderer=NewObject<UNiagaraMeshRendererProperties>(Instance.Emitter,NAME_None,RF_Transactional);
  FNiagaraMeshRendererMeshProperties Properties;Properties.Mesh=Mesh;Properties.Scale=FVector(MeshScale);
  Renderer->Meshes.Reset();Renderer->Meshes.Add(Properties);
  Instance.Emitter->AddRenderer(Renderer,Instance.Version);
  Renderer->CheckMaterialUsage();
 }
 System->RequestCompile(false);System->WaitForCompilationComplete();
 FAssetRegistryModule::AssetCreated(System);System->MarkPackageDirty();return System;
}

UStaticMesh* UFullsceneNiagaraLibrary::BakeFauna(USkeletalMeshComponent* Component,const FString& AssetPath) {
 if (!Component || !Component->IsRegistered() || !AssetPath.StartsWith(TEXT("/Game/FullsceneVFX/"))) return nullptr;
 if (auto* Existing=LoadObject<UStaticMesh>(nullptr,*AssetPath)) return Existing;
 TArray<UMeshComponent*> Components;Components.Add(Component);
 auto& Utilities=FModuleManager::LoadModuleChecked<IMeshUtilities>("MeshUtilities");
 return Utilities.ConvertMeshesToStaticMesh(Components,Component->GetComponentTransform(),AssetPath);
}

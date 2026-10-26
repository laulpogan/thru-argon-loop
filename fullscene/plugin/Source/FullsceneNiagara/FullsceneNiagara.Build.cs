using UnrealBuildTool;
public class FullsceneNiagara : ModuleRules {
 public FullsceneNiagara(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage=PCHUsageMode.UseExplicitOrSharedPCHs;
  PrivateDependencyModuleNames.AddRange(new string[]{"Core","CoreUObject","Engine","UnrealEd","Niagara","NiagaraEditor","AssetRegistry","MeshUtilities"});
 }
}

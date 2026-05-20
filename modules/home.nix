# Provides an option for declaring Home Manager configurations.
# These configurations end up as flake outputs under `#homeConfigurations."<name>"`.
# A check for the activation package of each configuration also ends
# under `#checks.<system>."configurations:home:<name>"`.
{ lib, config, inputs, ... }:
{
  options.configurations.home = lib.mkOption {
    type = lib.types.lazyAttrsOf (
      lib.types.submodule {
        options = {
          module = lib.mkOption {
            type = lib.types.deferredModule;
          };
          pkgs = lib.mkOption {
            type = lib.types.raw;
            description = "The instantiated nixpkgs (e.g., inputs.nixpkgs.legacyPackages.x86_64-linux) to use for this configuration.";
          };
        };
      }
    );
  };

  config.flake = {
    homeConfigurations = lib.flip lib.mapAttrs config.configurations.home (
      name: { module, pkgs }: inputs.home-manager.lib.homeManagerConfiguration {
        inherit pkgs;
        modules = [ module ];
      }
    );

    checks =
      config.flake.homeConfigurations
      |> lib.mapAttrsToList (
        name: hm: {
          # Safely extract the system from the provided pkgs instance
          ${hm.pkgs.stdenv.hostPlatform.system} = {
            "configurations:home:${name}" = hm.activationPackage;
          };
        }
      )
      |> lib.mkMerge;
  };
}
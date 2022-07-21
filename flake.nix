{
  description = "nixos-compose";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:

    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        app = pkgs.poetry2nix.mkPoetryApplication {
          projectDir = ./.;
          propagatedBuildInputs = [ ];
          editablePackageSources = {
             oar-plugins = ./src;
          };
        };
         overrides_oar = pkgs.poetry2nix.defaultPoetryOverrides.extend ( self: super: {
            oar = super.oar.overridePythonAttrs (
              old: {
                buildInputs = (old.buildInputs or [ ]) ++ [ self.poetry ];
              }
            );
          });
        packageName = "oar-plugins";
      in {
        packages.${packageName} = app;

        defaultPackage = self.packages.${system}.${packageName};

        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            (poetry2nix.mkPoetryEnv {
              projectDir = self;
              overrides = overrides_oar;
            })

            (poetry2nix.mkPoetryApplication {
              projectDir = self;
              overrides = overrides_oar;
            })
            poetry
            postgresql
            pre-commit
          ];
        };
    });
}
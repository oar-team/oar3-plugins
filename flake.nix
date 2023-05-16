{
  description = "nixos-compose";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = import nixpkgs {inherit system;};

      app = pkgs.poetry2nix.mkPoetryApplication {
        projectDir = ./.;
        propagatedBuildInputs = [];
        editablePackageSources = {
          oar-plugins = ./src;
        };
      };
      # https://github.com/nix-community/poetry2nix/blob/master/docs/edgecases.md#modulenotfounderror-no-module-named-poetry
      overrides_oar = pkgs.poetry2nix.defaultPoetryOverrides.extend (self: super: {
        oar = super.oar.overridePythonAttrs (
          old: {
            buildInputs = (old.buildInputs or []) ++ [self.poetry];
          }
        );
      });
      packageName = "oar-plugins";
    in {
      packages.${packageName} = app;

      defaultPackage = self.packages.${system}.${packageName};

      devShell = pkgs.mkShell {
        LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib";
        buildInputs = with pkgs; [
          # (poetry2nix.mkPoetryEnv {
          #   projectDir = self;
          #   overrides = overrides_oar;
          # })
          # # Install the project so that the entry_points can be found by oar
          # (poetry2nix.mkPoetryApplication {
          #   projectDir = self;
          #   overrides = overrides_oar;
          # })
          poetry
          postgresql
          pre-commit
        ];
      };
      formatter = nixpkgs.legacyPackages.x86_64-linux.alejandra;
    });
}

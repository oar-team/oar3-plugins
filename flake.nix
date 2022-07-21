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
             oar-plugins = ./.;
          };
        };

        packageName = "oar";
      in {
        packages.${packageName} = app;

        defaultPackage = self.packages.${system}.${packageName};

        devShell = pkgs.mkShell {
          buildInputs = with pkgs; [
            (poetry2nix.mkPoetryEnv { projectDir = self; })

            python3Packages.sphinx_rtd_theme
            poetry
            postgresql
            pre-commit
          ];
        };
    });
}

{
  description = "A stupid simple dev environment for Verifiable AI";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      # Support standard Linux and macOS architectures
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSystem = nixpkgs.lib.genAttrs supportedSystems;
    in
    {
      devShells = forEachSystem (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          
          # Define the Python environment with required packages
          pythonEnv = pkgs.python3.withPackages (ps: with ps; [
            torch
            transformers
            cryptography
          ]);
        in
        {
          default = pkgs.mkShell {
            packages = [ pythonEnv ];

            shellHook = ''
              echo "========================================="
              echo "  Verifiable AI Dev Environment Ready!   "
              echo "========================================="
              echo "Execute your script with:"
              echo "  python verifiable_ai.py"
            '';
          };
        }
      );
    };
}
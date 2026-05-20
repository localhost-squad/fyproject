{ lib, ... }:
let
  server_configuration = { pkgs, ... }: {
    
    # --- NIX CORE SETTINGS ---
    nix.settings = {
      experimental-features = [ "nix-command" "flakes" "pipe-operators" ];
      trusted-users = [ "root" "sudha" ];
    };
    programs.nix-ld.enable = true;
    nixpkgs.config.allowUnfree = true;

    # --- BOOT & HARDWARE ---
    boot = {
      kernelPackages = pkgs.linuxPackages_latest;
      loader.grub = {
        enable = true;
        efiSupport = false; # Explicitly disabling EFI for older BIOS
        # devices = [ "/dev/sda" ]; # <-- Uncomment this when installing to the MBR of the 500GB drive
      };
    };
    hardware.bluetooth.enable = true;

    # --- NETWORKING & SYSTEM ---
    networking = {
      hostName = "server"; 
      networkmanager.enable = true;
      firewall.enable = false;
    };
    time.timeZone = "Asia/Kolkata";
    i18n.defaultLocale = "en_US.UTF-8";
    console.keyMap = "us";

    # --- USERS ---
    users.users.sudha = {
      isNormalUser = true;
      extraGroups = [ "wheel" "dialout" "docker" ];
      openssh.authorizedKeys.keys = [
        "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIALJ8zFKvTUdkpoltZWDRBTRdKUrU9XLwaP4AWIMYGPM sudha@laptop"
      ];
    };

    # --- SERVICES ---
    services.avahi = {
      enable = true;
      nssmdns4 = true; # Allows the laptop (and all nodes) to resolve .local
      publish = {
        enable = true;
        addresses = true;
        workstation = true;
      };
    };
    
    # --- VIRTUALIZATION ---
    virtualisation.docker = {
      enable = true;
      daemon.settings = {
        "max-concurrent-downloads" = 1;
        "max-concurrent-uploads" = 1;
        "registry-mirrors" = []; # Ensures no interference
      };
    };

    # --- PACKAGES ---
    environment.systemPackages = with pkgs; [
      tree 
      util-linux 
      vim 
      wget 
      curl 
      git 
      gptfdisk 
      htop 
      pciutils 
      home-manager
      cloudflared
      sops
      age
      ssh-to-age
    ];
    
    system.stateVersion = "25.11"; 
  };

  # Map the module to the specific host
  targetHosts = [ "server" ];
in
{
  configurations.nixos = lib.genAttrs targetHosts (name: {
    module = server_configuration;
  });
}
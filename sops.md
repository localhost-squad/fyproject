This is the DevOps endgame. Setting up `sops-nix` for the first time takes a few steps, but once the foundation is laid, adding new secrets takes literally 10 seconds.

Here is the complete, step-by-step guide to locking down your NixOS server using your Cloudflare Tunnel token as the primary example.

---

### Step 1: Install the Encryption Tools

First, make sure your server has the tools needed to generate and translate the keys.

1. Add these to your `environment.systemPackages` in `configuration.nix`:
```nix
environment.systemPackages = with pkgs; [
  sops
  age
  ssh-to-age
];

```


2. Rebuild your system to install them:
```bash
sudo nixos-rebuild switch --flake .#server

```



---

### Step 2: Gather Your "Padlocks" (Public Keys)

You need two public keys: one for your server, and one for your personal user (so you can edit the files later).

1. **Convert the Server's SSH Key to Age format:**
Run this command in your terminal to translate your server's automatic SSH key into an `age` key:
```bash
ssh-to-age < /etc/ssh/ssh_host_ed25519_key.pub

```


*Copy the output. It will look like `age1server...*`
2. **Generate your Personal Admin Key:**
Run this to generate a personal key pair for your user (`sudha`). By putting it in `~/.config/sops/age/keys.txt`, SOPS will automatically detect it later.
```bash
mkdir -p ~/.config/sops/age
age-keygen -o ~/.config/sops/age/keys.txt

```


*The terminal will print your public key. Copy the output. It will look like `age1admin...*`

---

### Step 3: Tell SOPS the Rules (`.sops.yaml`)

Go to the root folder of your NixOS flake (where your `flake.nix` is). Create a file named exactly `.sops.yaml`. This tells SOPS which keys to use for encryption.

**Create `.sops.yaml`:**

```yaml
keys:
  # Paste the age1... key you got from age-keygen here
  - &admin_sudha age1admin_public_key_here
  # Paste the age1... key you got from ssh-to-age here
  - &server age1server_public_key_here

creation_rules:
  # This rule applies to any file in the 'secrets' folder
  - path_regex: secrets/.*
    key_groups:
    - age:
      - *admin_sudha
      - *server

```

---

### Step 4: Encrypt Your First Secret

Let's encrypt your Cloudflare Tunnel token.

1. Create a `secrets` directory in your flake folder:
```bash
mkdir secrets

```


2. Tell SOPS to create a new encrypted file. Because you are going to inject this into a Systemd environment, we will make it a `.env` file:
```bash
sops secrets/cloudflare.env

```


3. SOPS will open a text editor (usually `nano` or `vim`). Paste your secret in like this:
```env
TUNNEL_TOKEN=eyJh...[your_massive_cloudflare_token]...

```


4. Save and exit the editor. SOPS will instantly encrypt the file. If you run `cat secrets/cloudflare.env`, you will see a massive wall of encrypted gibberish. **It is now safe to commit to Git.**

---

### Step 5: Wire it into NixOS

Now, you create your `cloudflared.nix` module. This module will tell `sops-nix` to decrypt the file, and then pass it to the Cloudflare daemon.

**Create `cloudflared.nix` in your modules folder:**

```nix
{ config, pkgs, inputs, ... }: {

  # 1. Import the sops-nix module from your flake inputs
  imports = [ inputs.sops-nix.nixosModules.sops ];

  # 2. Configure SOPS
  sops = {
    # Tell sops-nix to use the server's SSH key to unlock the file
    age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];
    
    # Declare the specific secret file
    secrets."cloudflare.env" = {
      sopsFile = ../secrets/cloudflare.env;
      format = "dotenv";
    };
  };

  # 3. Create the robust Cloudflared Service
  systemd.services.cloudflared-tunnel = {
    description = "Cloudflared Remotely Managed Tunnel";
    wantedBy = [ "multi-user.target" ];
    after = [ "network-online.target" ];
    
    serviceConfig = {
      # The main executable
      ExecStart = "${pkgs.cloudflared}/bin/cloudflared tunnel --no-autoupdate run";
      
      # INJECT THE SECRET HERE: config.sops.secrets."name".path points to the decrypted RAM disk
      EnvironmentFile = config.sops.secrets."cloudflare.env".path;
      
      Restart = "always";
      RestartSec = "5s";
      DynamicUser = true; 
    };
  };
}

```

### Step 6: Deploy!

Make sure `cloudflared.nix` is imported in your `configuration.nix` (or `flake.nix` via `import-tree`), and then run your rebuild command:

```bash
sudo nixos-rebuild switch --flake .#server

```

**What just happened?**
NixOS built your system, `sops-nix` used your server's SSH key to secretly decrypt `cloudflare.env` into memory, and Systemd launched `cloudflared` using that memory file. Your tunnel is now live, and your Git repo contains zero plain-text passwords!
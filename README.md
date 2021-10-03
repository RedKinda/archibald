# Archibald

## Cross-compiling on raspberry pi
```bash
sudo apt install gcc-arm-linux-gnueabihf
rustup target add armv7-unknown-linux-gnueabihf
echo '''[target.armv7-unknown-linux-gnueabihf]
linker = "arm-linux-gnueabihf-gcc"''' > ./.cargo/config

# Main one
cargo build --release --target=armv7-unknown-linux-gnueabihf
```
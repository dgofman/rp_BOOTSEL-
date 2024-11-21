# Debugging with Picobrobe on Raspberry Pi Pico

This guide outlines how to set up debugging on your Raspberry Pi Pico using Picoprobe, OpenOCD, and GDB. You can follow the steps provided in the official [Raspberry Pi Pico Debugging with VS Code guide](https://www.digikey.com/en/maker/projects/raspberry-pi-pico-and-rp2040-cc-part-2-debugging-with-vs-code/470abc7efb07432b82c95f6f67f184c0), which provides a very detailed tutorial and video on how to implement remote debugging.

## Picoprobe Setup

If you're looking to upload files and perform debugging, you can use the Picoprobe interface. However, note that some users, including myself, have faced issues with the latest `picoprobe.uf2` release from [GitHub](https://github.com/raspberrypi/debugprobe/releases).

### Using the Picoprobe UF2

To check the build information for the Picoprobe firmware file, use the following command:
```bash
picotool info -a picoprobe.uf2
```
```yaml
Build Information
 sdk version:       1.0.1
 pico_board:        pico
 build date:        Feb  3 2021
 build attributes:  Release
```
If the latest Picoprobe firmware does not work for you, you can try using the version from my repo.

In **.vscode** changes allow you to use VSCode to compile, flash, and debug your program on the **Raspberry Pi Pico** across different projects.
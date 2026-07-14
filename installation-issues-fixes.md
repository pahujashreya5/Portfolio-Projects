I use a Mac M2, and the installation of OpenUSD for MacOS involes cloning a Github repo. This can lead to lots of version and installation issues.

1. xcode
In case you keep getting the error that xcode is required even though your command line tools are isntalled, you don't need to install the full app. Run the below code in your terminal. This gives a fake response to the repo, which is trying to run a check for xcode app installation, even though the official readme says that CLI tools will work. After this, the build script command should work.

```
mkdir -p ~/.xcode_hack
cat << 'EOF' > ~/.xcode_hack/xcodebuild
#!/bin/bash
echo "Xcode 15.0"
echo "Build version 15A240d"
EOF
chmod +x ~/.xcode_hack/xcodebuild
export PATH="$HOME/.xcode_hack:$PATH"
```

2. Another issue I faced (and this might just be me) was with software updates. I had a full software update for my OS that was pending, only after I installed it did the xcode CLI install and get recognized properly. Note that after updates, you might have to reset or even reinstall some tools so going over the installation from scratch would save you time.

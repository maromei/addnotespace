#!/bin/bash

version=$(hatch version)
dir_name="addnotespace_v${version}_x86_linux"
build_path="build/${dir_name}"

cp -r ui_files $build_path

cd $build_path

zip "../${dir_name}.zip" * -r

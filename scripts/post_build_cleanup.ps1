$version = hatch version
$build_path = "build/addnotespace_v$($version)_x86"

copy -r ui_files $build_path
mv "$($build_path)/main.exe" "$($build_path)/addnotespace.exe"

Compress-Archive -Path $build_path -DestinationPath "$($build_path).zip" -CompressionLevel "Optimal"
$version = hatch version
$build_path = "build/addnotespace_v$($version)_x86_win32"

copy -r ui_files $build_path

Compress-Archive -Path $build_path -DestinationPath "$($build_path).zip" -CompressionLevel "Optimal"

$version = <hatch version>
$build_path = "build/addnotespace_v$($version)_x86"

copy -r ui_files $build_path
copy -r env_files $build_path

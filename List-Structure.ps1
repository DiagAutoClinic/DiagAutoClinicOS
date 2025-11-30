param(
    [string]$Path = "."
)

Write-Host "Structure for highlighted root items in: $Path"
Write-Host "--------------------------------------------------------"

# Allowed file extensions
$allowed = ".py", ".txt", ".md"

# Get all top-level items (only first level)
$top = Get-ChildItem -Path $Path

foreach ($item in $top) {

    if ($item.PSIsContainer) {
        # Directory
        Write-Host "+-- $($item.Name)/"

        # List only allowed files directly inside the folder
        $subfiles = Get-ChildItem -Path $item.FullName -File | Where-Object {
            $_.Extension -in $allowed
        }

        foreach ($sf in $subfiles) {
            Write-Host "    +-- $($sf.Name)"
        }
    }
    else {
        # File: include only allowed types
        if ($item.Extension -in $allowed) {
            Write-Host "+-- $($item.Name)"
        }
    }
}

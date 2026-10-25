# drive-organizer helpers. Dot-source:  . .\helpers.ps1
# Windows PowerShell 5.1 compatible. Names avoid built-in aliases (Mv, Set, Cp ...).

$script:AuditDir = $null
$script:Log      = New-Object System.Collections.Generic.List[object]
$script:Manifest = New-Object System.Collections.Generic.List[object]

function Initialize-Audit {
    param([Parameter(Mandatory)][string]$Drive, [string]$Date = (Get-Date -Format 'yyyy-MM-dd'))
    $script:AuditDir = "${Drive}:\_Drive-Audit-$Date"
    New-Item -ItemType Directory -Force -Path $script:AuditDir | Out-Null
    $script:ReviewDir = "${Drive}:\To Delete - Review Before Deletion"
    "Audit folder: $script:AuditDir"
}

function Get-FolderSummary {
    # One line per top-level folder: files, size, newest file.
    param([string]$Root, [string[]]$Skip = @('$RECYCLE.BIN', 'System Volume Information'))
    Get-ChildItem $Root -Directory -Force | Where-Object { $_.Name -notin $Skip } | ForEach-Object {
        $f = Get-ChildItem $_.FullName -Recurse -File -Force -ErrorAction SilentlyContinue
        [pscustomobject]@{
            Folder = $_.Name
            Files  = ($f | Measure-Object).Count
            GB     = [math]::Round((($f | Measure-Object Length -Sum).Sum) / 1GB, 2)
            Newest = ($f | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
        }
    }
}

function Get-GitRoots {
    # A .git DIRECTORY = repo. A .git FILE = worktree (has an absolute gitdir path - do not move).
    param([string[]]$Roots, [int]$Depth = 4)
    Get-ChildItem $Roots -Recurse -Force -Depth $Depth -Filter .git -ErrorAction SilentlyContinue | ForEach-Object {
        $kind = if ($_.PSIsContainer) { 'repo' } else { 'WORKTREE: ' + (Get-Content $_.FullName -TotalCount 1) }
        [pscustomobject]@{ Path = $_.FullName; Kind = $kind }
    }
}

function Get-ReparsePoints {
    param([string]$Root, [int]$Depth = 4)
    Get-ChildItem $Root -Recurse -Force -Attributes ReparsePoint -Depth $Depth -ErrorAction SilentlyContinue |
        Select-Object FullName, LinkType, Target
}

function Find-DuplicateFiles {
    # Exact duplicates only: group by size, then SHA-256. Returns Hash/Path/Length rows.
    param([string[]]$Roots, [string[]]$ExcludeRegex = @('\\(\.git|node_modules|\.vs|bin|obj)\\'))
    $files = Get-ChildItem -LiteralPath $Roots -Recurse -File -Force -ErrorAction SilentlyContinue |
        Where-Object { $p = $_.FullName; -not ($ExcludeRegex | Where-Object { $p -match $_ }) -and $_.Length -gt 0 }
    $bySize = $files | Group-Object Length | Where-Object Count -gt 1
    $rows = foreach ($g in $bySize) {
        foreach ($f in $g.Group) {
            $h = Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256 -ErrorAction SilentlyContinue
            if ($h) { [pscustomobject]@{ Hash = $h.Hash; Path = $f.FullName; Length = $f.Length; Modified = $f.LastWriteTime } }
        }
    }
    $rows | Group-Object Hash | Where-Object Count -gt 1 | ForEach-Object {
        # Keep-first ordering: names without "(1)", "- Copy", "Backup" first, then oldest.
        $sorted = $_.Group | Sort-Object @{ e = { if ($_.Path -match '\(\d+\)|- Copy|\\Backup\\') { 1 } else { 0 } } }, Modified
        [pscustomobject]@{ Hash = $_.Name; Keep = $sorted[0].Path; Extras = @($sorted | Select-Object -Skip 1 | ForEach-Object Path); Bytes = $sorted[0].Length }
    }
}

function Compare-ZipToFolder {
    # Is a zip redundant? Compares entry path + size to an extracted folder (tries with/without the top-level prefix).
    param([string]$Zip, [string]$Folder)
    Add-Type -AssemblyName System.IO.Compression.FileSystem
    $z = [IO.Compression.ZipFile]::OpenRead($Zip)
    $entries = $z.Entries | Where-Object { $_.Name }
    $best = $null
    foreach ($strip in 0, 1) {
        $match = 0; $same = 0
        foreach ($e in $entries) {
            $rel = $e.FullName.Replace('/', '\')
            if ($strip) { $i = $rel.IndexOf('\'); if ($i -lt 0) { continue }; $rel = $rel.Substring($i + 1) }
            $p = Join-Path $Folder $rel
            if (Test-Path -LiteralPath $p) { $match++; if ((Get-Item -LiteralPath $p -Force).Length -eq $e.Length) { $same++ } }
        }
        if (-not $best -or $same -gt $best.SameSize) { $best = [pscustomobject]@{ Entries = $entries.Count; InFolder = $match; SameSize = $same; Missing = $entries.Count - $match } }
    }
    $z.Dispose(); $best
}

function Get-ShortcutTargets {
    # Find .lnk files whose target matches a regex (e.g. paths you are about to move).
    param([string[]]$Roots, [string]$TargetRegex = '.')
    $w = New-Object -ComObject WScript.Shell
    Get-ChildItem $Roots -Recurse -Filter *.lnk -Force -ErrorAction SilentlyContinue | ForEach-Object {
        $l = $w.CreateShortcut($_.FullName)
        if ($l.TargetPath -match $TargetRegex) { [pscustomobject]@{ Shortcut = $_.FullName; Target = $l.TargetPath; Args = $l.Arguments } }
    }
}

function Set-ShortcutTarget {
    param([string]$Shortcut, [string]$NewTarget)
    $w = New-Object -ComObject WScript.Shell
    $l = $w.CreateShortcut($Shortcut); $old = $l.TargetPath
    $l.TargetPath = $NewTarget; $l.WorkingDirectory = Split-Path $NewTarget; $l.Save()
    Add-LogRow -Original "$Shortcut (target $old)" -New "target $NewTarget" -Category 'shortcut' -Status 'SHORTCUT-FIXED'
}

function Add-LogRow { param($Original, $New, $Category, $Status)
    $script:Log.Add([pscustomobject]@{ Original = $Original; New = $New; Category = $Category; Status = $Status }) }

function Get-ItemBytes { param([string]$Path)
    $i = Get-Item -LiteralPath $Path -Force
    if ($i.PSIsContainer) { (Get-ChildItem -LiteralPath $Path -Recurse -File -Force -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum } else { $i.Length } }

function Move-Safe {
    # Never overwrites. Creates parent folders. Verifies size afterwards. Logs. Optionally adds a manifest row.
    param([Parameter(Mandatory)][string]$Source, [Parameter(Mandatory)][string]$Destination,
          [string]$Category = 'move', [string]$Reason, [switch]$Suffix)
    if (-not (Test-Path -LiteralPath $Source)) { Add-LogRow $Source $Destination $Category 'SKIP-missing'; return }
    if (Test-Path -LiteralPath $Destination) {
        if ($Suffix) {
            $n = [IO.Path]::GetFileNameWithoutExtension($Destination); $e = [IO.Path]::GetExtension($Destination)
            $Destination = Join-Path (Split-Path $Destination) "$n (moved)$e"
        }
        if (Test-Path -LiteralPath $Destination) { Add-LogRow $Source $Destination $Category 'SKIP-destination-exists'; return }
    }
    $before = Get-ItemBytes $Source
    New-Item -ItemType Directory -Force -Path (Split-Path $Destination) | Out-Null
    try {
        Move-Item -LiteralPath $Source -Destination $Destination -ErrorAction Stop
        $status = if ((Get-ItemBytes $Destination) -eq $before) { 'MOVED' } else { 'MOVED-SIZE-MISMATCH' }
        if ($Reason) { $script:Manifest.Add([pscustomobject]@{ Original = $Source; New = $Destination; Reason = $Reason; SizeBytes = $before; Uncertainty = 'Low' }) }
    } catch { $status = "FAILED: $($_.Exception.Message)" }
    Add-LogRow $Source $Destination $Category $status
}

function Move-ToReview {
    # Keeps the original relative path under the review folder (drive letter stripped).
    param([string]$Source, [string]$Reason)
    $rel = if ($Source -match '^[A-Za-z]:\\') { $Source.Substring(3) } else { Split-Path $Source -Leaf }
    Move-Safe -Source $Source -Destination (Join-Path $script:ReviewDir $rel) -Category 'review' -Reason $Reason
}

function Save-Audit {
    # Appends to the CSVs so several runs accumulate.
    $script:Log      | Export-Csv "$script:AuditDir\MOVE-LOG.csv" -NoTypeInformation -Append
    if ($script:Manifest.Count) { $script:Manifest | Export-Csv "$script:AuditDir\MANIFEST-To-Delete.csv" -NoTypeInformation -Append }
    $script:Log | Group-Object Status | ForEach-Object { '{0}: {1}' -f $_.Name, $_.Count }
    $script:Log.Clear(); $script:Manifest.Clear()
}

function Test-AuditLog {
    # Phase 4: every MOVED row exists at its destination (or in the review folder if the user deleted it later).
    $rows = Import-Csv "$script:AuditDir\MOVE-LOG.csv" | Where-Object Status -like 'MOVED*'
    $gone = $rows | Where-Object { -not (Test-Path -LiteralPath $_.New) }
    $left = $rows | Where-Object { Test-Path -LiteralPath $_.Original }
    "rows: $($rows.Count); missing at destination: $(@($gone).Count); still at origin: $(@($left).Count)"
}

function Get-EmptyFolders {
    param([string[]]$Roots)
    Get-ChildItem $Roots -Recurse -Directory -Force -ErrorAction SilentlyContinue |
        Where-Object { -not (Get-ChildItem $_.FullName -Force -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 1) } |
        ForEach-Object FullName
}

function Get-FileKind {
    # Magic-number sniff for extension-less downloads.
    param([string]$Path)
    $b = [IO.File]::ReadAllBytes($Path)[0..7]; $hex = ($b | ForEach-Object { '{0:X2}' -f $_ }) -join ' '
    switch -Regex ($hex) { '^89 50 4E 47' { 'png' } '^25 50 44 46' { 'pdf' } '^50 4B 03 04' { 'zip/docx/xlsx' } '^FF D8 FF' { 'jpg' } default { 'unknown' } }
}

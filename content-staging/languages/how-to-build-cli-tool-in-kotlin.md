---
title: "Build a CLI Tool in Kotlin — A Step-by-Step Tutorial"
description: "Build a working command-line file organizer in Kotlin to learn argument parsing, file I/O, and structured output hands-on."
published_date: "2026-04-22"
category: "languages"
language: "kotlin"
concept: "cli-tool"
template_id: "lang-v5"
tags: ["kotlin", "cli-tool", "tutorial", "command-line"]
difficulty: "intermediate"
related_posts:
  - /languages/kotlin/data-classes
  - /languages/kotlin/coroutines
  - /languages/kotlin/extension-functions
related_tools:
  - /tools/kotlin-playground
og_image: "/og/languages/kotlin/cli-tool.png"
---

By the end of this tutorial, you will have a working command-line file organizer written in Kotlin that scans a directory, categorizes files by extension, and generates a summary report — a practical tool you can use immediately and extend for your own workflows.

## What You'll Build

The project is called **FileSort** — a CLI tool that accepts a directory path as an argument, scans all files in that directory, categorizes them into groups (images, documents, code, archives, and other), and outputs a formatted summary table showing the file count and total size for each category. The tool also supports a `--move` flag that physically moves files into category-specific subdirectories.

This mini-project demonstrates several core Kotlin concepts: command-line argument parsing, file system operations using `java.io.File` and `kotlin.io` extensions, data classes for structuring intermediate results, sealed classes for representing categories, and formatted string output. The build is fully self-contained — no external dependencies beyond the Kotlin standard library and the JVM's `java.io` package.

**Prerequisites:** Basic Kotlin syntax, familiarity with functions and classes, and a Kotlin development environment (IntelliJ IDEA or `kotlinc` CLI compiler).

## Step 1 — Parse Command-Line Arguments

```kotlin
import java.io.File

// Data class to hold parsed CLI arguments
data class CliArgs(
    val targetDir: File,
    val shouldMove: Boolean,
    val verbose: Boolean
)

// Parse raw command-line arguments into a structured CliArgs object
fun parseArgs(args: Array<String>): CliArgs {
    if (args.isEmpty()) {
        System.err.println("Usage: filesort <directory> [--move] [--verbose]")
        System.err.println("  <directory>  Path to the directory to organize")
        System.err.println("  --move       Move files into category subdirectories")
        System.err.println("  --verbose    Print detailed file-by-file output")
        kotlin.system.exitProcess(1)
    }

    val targetDir = File(args[0])
    val flags = args.drop(1).toSet()

    // Validate the target directory exists and is readable
    require(targetDir.exists()) { "Directory does not exist: ${targetDir.absolutePath}" }
    require(targetDir.isDirectory) { "Not a directory: ${targetDir.absolutePath}" }

    return CliArgs(
        targetDir = targetDir,
        shouldMove = "--move" in flags,
        verbose = "--verbose" in flags
    )
}
```

This first step establishes the CLI's entry point contract. The `CliArgs` data class provides a type-safe container for parsed arguments — Kotlin's data classes automatically generate `equals()`, `hashCode()`, `toString()`, and `copy()` methods, making them ideal for configuration objects. The `parseArgs` function validates inputs eagerly: it prints usage instructions when no arguments are provided and uses Kotlin's `require()` function (which throws `IllegalArgumentException` on failure) to ensure the target path exists and is a directory. The `args.drop(1).toSet()` pattern efficiently separates the required positional argument from optional flags. This validation-first approach prevents cryptic errors later in the pipeline when the tool attempts to read from a nonexistent directory.

## Step 2 — Define File Categories with Sealed Classes

```kotlin
// Sealed class represents all possible file categories — compiler enforces exhaustive handling
sealed class FileCategory(val label: String, val dirName: String) {
    object Images : FileCategory("Images", "images")
    object Documents : FileCategory("Documents", "documents")
    object Code : FileCategory("Code", "code")
    object Archives : FileCategory("Archives", "archives")
    object Other : FileCategory("Other", "other")

    companion object {
        // Map file extensions to categories
        private val extensionMap = mapOf(
            // Images
            "jpg" to Images, "jpeg" to Images, "png" to Images,
            "gif" to Images, "svg" to Images, "webp" to Images, "bmp" to Images,
            // Documents
            "pdf" to Documents, "doc" to Documents, "docx" to Documents,
            "txt" to Documents, "md" to Documents, "csv" to Documents, "xlsx" to Documents,
            // Code
            "kt" to Code, "java" to Code, "py" to Code, "js" to Code,
            "ts" to Code, "go" to Code, "rs" to Code, "cpp" to Code,
            "html" to Code, "css" to Code, "json" to Code, "xml" to Code,
            // Archives
            "zip" to Archives, "tar" to Archives, "gz" to Archives,
            "rar" to Archives, "7z" to Archives
        )

        // Categorize a file based on its extension
        fun fromExtension(extension: String): FileCategory {
            return extensionMap[extension.lowercase()] ?: Other
        }

        // All categories for iteration
        fun all(): List<FileCategory> = listOf(Images, Documents, Code, Archives, Other)
    }
}
```

The sealed class hierarchy is the architectural backbone of the file categorizer. Kotlin's sealed classes restrict which subclasses can exist — all variants must be defined in the same file, and the compiler can verify that `when` expressions (Kotlin's equivalent of `match`/`switch`) handle every variant without a catch-all. This means if you later add a `Videos` category, every `when` block that matches on `FileCategory` will produce a compiler error until you add the new case. The `companion object` houses the extension-to-category mapping and a factory method, keeping categorization logic encapsulated within the type itself. The `fromExtension` method defaults to `Other` for unrecognized extensions — a safe fallback that prevents the tool from crashing on unexpected file types.

## Step 3 — Scan Directory and Build the Report

```kotlin
// Data class for individual file information
data class FileInfo(
    val name: String,
    val extension: String,
    val sizeBytes: Long,
    val category: FileCategory
)

// Data class for category-level summary
data class CategorySummary(
    val category: FileCategory,
    val fileCount: Int,
    val totalSizeBytes: Long,
    val files: List<FileInfo>
)

// Scan the target directory and produce categorized summaries
fun scanDirectory(targetDir: File): List<CategorySummary> {
    // List only files (not subdirectories), skip hidden files
    val files = targetDir.listFiles()
        ?.filter { it.isFile && !it.name.startsWith(".") }
        ?: emptyList()

    // Map each file to a FileInfo object with its category
    val fileInfos = files.map { file ->
        FileInfo(
            name = file.name,
            extension = file.extension,
            sizeBytes = file.length(),
            category = FileCategory.fromExtension(file.extension)
        )
    }

    // Group by category and build summaries
    return FileCategory.all().map { category ->
        val categoryFiles = fileInfos.filter { it.category == category }
        CategorySummary(
            category = category,
            fileCount = categoryFiles.size,
            totalSizeBytes = categoryFiles.sumOf { it.sizeBytes },
            files = categoryFiles
        )
    }.filter { it.fileCount > 0 } // Only include categories with files
}

// Format byte sizes into human-readable strings
fun formatSize(bytes: Long): String {
    return when {
        bytes >= 1_073_741_824 -> "%.1f GB".format(bytes / 1_073_741_824.0)
        bytes >= 1_048_576 -> "%.1f MB".format(bytes / 1_048_576.0)
        bytes >= 1_024 -> "%.1f KB".format(bytes / 1_024.0)
        else -> "$bytes B"
    }
}
```

The scanning step leverages Kotlin's functional collection operations to transform raw file system data into structured summaries. The `listFiles()` method returns a nullable array (it returns `null` if the path is not a directory or if an I/O error occurs), which Kotlin handles with the safe-call operator `?.` and the elvis operator `?: emptyList()`. The `map` and `filter` chain processes each file into a `FileInfo` object, categorizes it, and then groups results by category. The `sumOf` function computes total sizes within each category. The `formatSize` utility uses Kotlin's `when` expression — an expression-based conditional that returns values — to select the appropriate unit. Notice that the entire pipeline is immutable: no mutable lists, no counters, no loop variables. Each transformation creates new collections from existing ones, making the data flow explicit and easy to test in isolation.

## Step 4 — Handle File Moving and Error Cases

```kotlin
// Move files into category-specific subdirectories
fun moveFiles(targetDir: File, summaries: List<CategorySummary>): Map<String, Int> {
    val results = mutableMapOf<String, Int>()

    for (summary in summaries) {
        val categoryDir = File(targetDir, summary.category.dirName)

        // Create category subdirectory if it doesn't exist
        if (!categoryDir.exists()) {
            val created = categoryDir.mkdirs()
            if (!created) {
                System.err.println("Warning: Could not create directory: ${categoryDir.absolutePath}")
                continue
            }
        }

        var movedCount = 0
        for (fileInfo in summary.files) {
            val sourceFile = File(targetDir, fileInfo.name)
            val destFile = File(categoryDir, fileInfo.name)

            try {
                // Check for naming conflicts
                if (destFile.exists()) {
                    System.err.println("  Skipped (exists): ${fileInfo.name}")
                    continue
                }

                // Move the file
                val success = sourceFile.renameTo(destFile)
                if (success) {
                    movedCount++
                } else {
                    // renameTo fails across filesystems — fall back to copy + delete
                    sourceFile.copyTo(destFile, overwrite = false)
                    sourceFile.delete()
                    movedCount++
                }
            } catch (e: Exception) {
                System.err.println("  Error moving ${fileInfo.name}: ${e.message}")
            }
        }

        results[summary.category.label] = movedCount
    }

    return results
}

// Print the formatted summary report to stdout
fun printReport(summaries: List<CategorySummary>, verbose: Boolean) {
    val totalFiles = summaries.sumOf { it.fileCount }
    val totalSize = summaries.sumOf { it.totalSizeBytes }

    println("┌────────────┬───────┬────────────┐")
    println("│ Category   │ Files │ Total Size │")
    println("├────────────┼───────┼────────────┤")

    for (summary in summaries) {
        val cat = summary.category.label.padEnd(10)
        val count = summary.fileCount.toString().padStart(5)
        val size = formatSize(summary.totalSizeBytes).padStart(10)
        println("│ $cat │$count │$size │")

        // In verbose mode, list individual files under each category
        if (verbose) {
            for (file in summary.files.sortedByDescending { it.sizeBytes }) {
                val fname = file.name.take(30).padEnd(30)
                val fsize = formatSize(file.sizeBytes).padStart(10)
                println("│   └─ $fname  $fsize │")
            }
        }
    }

    println("├────────────┼───────┼────────────┤")
    val totalLabel = "TOTAL".padEnd(10)
    val totalCount = totalFiles.toString().padStart(5)
    val totalSizeStr = formatSize(totalSize).padStart(10)
    println("│ $totalLabel │$totalCount │$totalSizeStr │")
    println("└────────────┴───────┴────────────┘")
}
```

The `moveFiles` function handles the messy reality of file system operations. The `renameTo` method in Java (and by extension Kotlin) is notoriously unreliable — it returns `false` instead of throwing an exception when the operation fails, and it silently fails when moving files across different filesystem mount points. The fallback path (`copyTo` + `delete`) handles the cross-filesystem case. Each potential failure point is handled individually: directory creation failure skips the entire category, naming conflicts skip individual files, and exceptions during copy/delete are caught and reported without aborting the entire operation. The `printReport` function uses Kotlin's string padding methods (`padEnd`, `padStart`) to produce aligned table output with Unicode box-drawing characters, giving the tool a professional appearance in the terminal.

## The Complete Code

```kotlin
import java.io.File
import kotlin.system.exitProcess

// ─── Data Models ──────────────────────────────────────────────

data class CliArgs(
    val targetDir: File,
    val shouldMove: Boolean,
    val verbose: Boolean
)

sealed class FileCategory(val label: String, val dirName: String) {
    object Images : FileCategory("Images", "images")
    object Documents : FileCategory("Documents", "documents")
    object Code : FileCategory("Code", "code")
    object Archives : FileCategory("Archives", "archives")
    object Other : FileCategory("Other", "other")

    companion object {
        private val extensionMap = mapOf(
            "jpg" to Images, "jpeg" to Images, "png" to Images,
            "gif" to Images, "svg" to Images, "webp" to Images, "bmp" to Images,
            "pdf" to Documents, "doc" to Documents, "docx" to Documents,
            "txt" to Documents, "md" to Documents, "csv" to Documents, "xlsx" to Documents,
            "kt" to Code, "java" to Code, "py" to Code, "js" to Code,
            "ts" to Code, "go" to Code, "rs" to Code, "cpp" to Code,
            "html" to Code, "css" to Code, "json" to Code, "xml" to Code,
            "zip" to Archives, "tar" to Archives, "gz" to Archives,
            "rar" to Archives, "7z" to Archives
        )

        fun fromExtension(extension: String): FileCategory =
            extensionMap[extension.lowercase()] ?: Other

        fun all(): List<FileCategory> = listOf(Images, Documents, Code, Archives, Other)
    }
}

data class FileInfo(
    val name: String,
    val extension: String,
    val sizeBytes: Long,
    val category: FileCategory
)

data class CategorySummary(
    val category: FileCategory,
    val fileCount: Int,
    val totalSizeBytes: Long,
    val files: List<FileInfo>
)

// ─── Core Functions ───────────────────────────────────────────

fun parseArgs(args: Array<String>): CliArgs {
    if (args.isEmpty()) {
        System.err.println("Usage: filesort <directory> [--move] [--verbose]")
        System.err.println("  <directory>  Path to the directory to organize")
        System.err.println("  --move       Move files into category subdirectories")
        System.err.println("  --verbose    Print detailed file-by-file output")
        exitProcess(1)
    }

    val targetDir = File(args[0])
    val flags = args.drop(1).toSet()

    require(targetDir.exists()) { "Directory does not exist: ${targetDir.absolutePath}" }
    require(targetDir.isDirectory) { "Not a directory: ${targetDir.absolutePath}" }

    return CliArgs(
        targetDir = targetDir,
        shouldMove = "--move" in flags,
        verbose = "--verbose" in flags
    )
}

fun scanDirectory(targetDir: File): List<CategorySummary> {
    val files = targetDir.listFiles()
        ?.filter { it.isFile && !it.name.startsWith(".") }
        ?: emptyList()

    val fileInfos = files.map { file ->
        FileInfo(
            name = file.name,
            extension = file.extension,
            sizeBytes = file.length(),
            category = FileCategory.fromExtension(file.extension)
        )
    }

    return FileCategory.all().map { category ->
        val categoryFiles = fileInfos.filter { it.category == category }
        CategorySummary(
            category = category,
            fileCount = categoryFiles.size,
            totalSizeBytes = categoryFiles.sumOf { it.sizeBytes },
            files = categoryFiles
        )
    }.filter { it.fileCount > 0 }
}

fun formatSize(bytes: Long): String = when {
    bytes >= 1_073_741_824 -> "%.1f GB".format(bytes / 1_073_741_824.0)
    bytes >= 1_048_576 -> "%.1f MB".format(bytes / 1_048_576.0)
    bytes >= 1_024 -> "%.1f KB".format(bytes / 1_024.0)
    else -> "$bytes B"
}

fun moveFiles(targetDir: File, summaries: List<CategorySummary>): Map<String, Int> {
    val results = mutableMapOf<String, Int>()
    for (summary in summaries) {
        val categoryDir = File(targetDir, summary.category.dirName)
        if (!categoryDir.exists() && !categoryDir.mkdirs()) {
            System.err.println("Warning: Could not create directory: ${categoryDir.absolutePath}")
            continue
        }
        var movedCount = 0
        for (fileInfo in summary.files) {
            val sourceFile = File(targetDir, fileInfo.name)
            val destFile = File(categoryDir, fileInfo.name)
            try {
                if (destFile.exists()) {
                    System.err.println("  Skipped (exists): ${fileInfo.name}")
                    continue
                }
                if (!sourceFile.renameTo(destFile)) {
                    sourceFile.copyTo(destFile, overwrite = false)
                    sourceFile.delete()
                }
                movedCount++
            } catch (e: Exception) {
                System.err.println("  Error moving ${fileInfo.name}: ${e.message}")
            }
        }
        results[summary.category.label] = movedCount
    }
    return results
}

fun printReport(summaries: List<CategorySummary>, verbose: Boolean) {
    val totalFiles = summaries.sumOf { it.fileCount }
    val totalSize = summaries.sumOf { it.totalSizeBytes }

    println("┌────────────┬───────┬────────────┐")
    println("│ Category   │ Files │ Total Size │")
    println("├────────────┼───────┼────────────┤")
    for (summary in summaries) {
        val cat = summary.category.label.padEnd(10)
        val count = summary.fileCount.toString().padStart(5)
        val size = formatSize(summary.totalSizeBytes).padStart(10)
        println("│ $cat │$count │$size │")
        if (verbose) {
            for (file in summary.files.sortedByDescending { it.sizeBytes }) {
                val fname = file.name.take(30).padEnd(30)
                val fsize = formatSize(file.sizeBytes).padStart(10)
                println("│   └─ $fname  $fsize │")
            }
        }
    }
    println("├────────────┼───────┼────────────┤")
    println("│ ${"TOTAL".padEnd(10)} │${totalFiles.toString().padStart(5)} │${formatSize(totalSize).padStart(10)} │")
    println("└────────────┴───────┴────────────┘")
}

// ─── Entry Point ──────────────────────────────────────────────

fun main(args: Array<String>) {
    val cliArgs = parseArgs(args)

    println("FileSort — Scanning: ${cliArgs.targetDir.absolutePath}")
    println()

    val summaries = scanDirectory(cliArgs.targetDir)

    if (summaries.isEmpty()) {
        println("No files found in the target directory.")
        return
    }

    printReport(summaries, cliArgs.verbose)

    if (cliArgs.shouldMove) {
        println()
        println("Moving files into category directories...")
        val results = moveFiles(cliArgs.targetDir, summaries)
        for ((category, count) in results) {
            println("  ✓ $category: $count files moved")
        }
        println("Done.")
    }
}
```

## Under the Hood: Performance & Mechanics

Kotlin compiles to JVM bytecode, and CLI tool performance on the JVM has characteristics that differ significantly from native-compiled languages like Rust or Go. The most impactful factor is JVM startup time — the `java` process must load the JVM itself, initialize the class loader, load Kotlin's standard library classes, and JIT-compile hot methods. For a simple CLI tool, this startup overhead is typically 200-500 milliseconds, which is noticeable compared to the near-instant startup of native binaries.

The file system scanning operation (`listFiles()`) delegates to the JVM's `java.io.File` implementation, which on most operating systems makes a single system call to read the directory entries. The time complexity is O(n) where n is the number of files in the directory. The subsequent `filter`, `map`, and `groupBy` operations each iterate the list once, maintaining O(n) overall complexity but with a constant factor multiplied by the number of transformation passes. For directories with thousands of files, this is negligible. For directories with hundreds of thousands of entries, consider using `java.nio.file.Files.newDirectoryStream()` which provides lazy iteration rather than loading all entries into memory at once.

Memory allocation in the scanning pipeline creates several intermediate lists — the `filter` creates a new list, `map` creates another, and each `CategorySummary` holds its own file list. For a directory with 10,000 files, this means approximately 5 list allocations with total memory usage proportional to n. The JVM's generational garbage collector handles these short-lived objects efficiently, promoting them through eden space and collecting them in minor GC pauses that are typically under 1 millisecond.

The `renameTo` method's performance depends entirely on the underlying operating system. On the same filesystem, a rename is an O(1) metadata operation — the file's data blocks are not copied, only the directory entry is updated. Cross-filesystem moves require a full data copy (O(n) where n is file size) followed by deletion of the source. Kotlin's `copyTo` extension function buffers the copy in 8KB chunks by default, which is efficient for most file sizes but suboptimal for very large files where a larger buffer would reduce system call overhead.

Kotlin's sealed class hierarchy compiles to an abstract Java class with static inner subclasses. The `when` expression over sealed class instances compiles to an `if-else` chain comparing class identity (using `instanceof` checks), which the JIT compiler optimizes to virtual dispatch or type ID comparison after warm-up. The extension map lookup is a standard `HashMap.get()` call — O(1) amortized time with String keys using the built-in hash function.

## Advanced Edge Cases

**Edge Case 1: Symlinks and circular directory references**

```kotlin
import java.nio.file.Files
import java.nio.file.Path

fun isSymlink(file: File): Boolean {
    return Files.isSymbolicLink(file.toPath())
}

// In the scanDirectory function, add symlink detection:
fun scanDirectorySafe(targetDir: File): List<CategorySummary> {
    val files = targetDir.listFiles()
        ?.filter { it.isFile && !it.name.startsWith(".") && !isSymlink(it) }
        ?: emptyList()

    // Without the symlink check, a symlink pointing to a file outside the
    // target directory would be categorized and potentially MOVED, which
    // breaks the symbolic link and can cause data loss in the linked location.
    // A symlink to a directory that points back to a parent directory
    // could cause infinite recursion if the tool supported recursive scanning.

    // ... rest of scanning logic
    return emptyList() // placeholder
}
```

Symbolic links present a subtle but dangerous edge case for file organization tools. The `listFiles()` method follows symlinks transparently — a symlink to a file appears as a regular file with `isFile` returning `true`. If the `--move` flag is active, `renameTo` on a symlink moves the link itself (not the target), but `copyTo` follows the link and copies the target's data, creating a regular file at the destination. This inconsistency between `renameTo` and `copyTo` means the fallback path produces different results than the primary path. On Linux and macOS systems where symlinks are common (especially in development directories with `node_modules` or Python virtual environments), this edge case can cause unexpected file duplication or broken links.

**Edge Case 2: Files with no extension or multiple dots**

```kotlin
fun main() {
    // Kotlin's File.extension property returns the text after the LAST dot
    val regular = File("report.pdf")
    println(regular.extension)  // "pdf"

    val multiple = File("backup.2026-04-22.tar.gz")
    println(multiple.extension)  // "gz" — only the last extension

    val noExtension = File("Makefile")
    println(noExtension.extension)  // "" — empty string

    val dotFile = File(".gitignore")
    println(dotFile.extension)  // "gitignore" — treats dot prefix as name separator

    val trailingDot = File("readme.")
    println(trailingDot.extension)  // "" — empty string after the dot

    // Problem: ".gitignore" gets categorized as "Other" (no "gitignore" in extensionMap)
    // Problem: "backup.tar.gz" gets categorized as Archives (correct)
    //          but "backup.tar" also gets Archives (correct coincidence)
    // Problem: "Makefile" gets categorized as Other — might want "Code" for known names
}
```

Kotlin's `File.extension` property splits on the last dot, which produces correct results for simple filenames but creates ambiguity for compound extensions like `.tar.gz`, dotfiles like `.gitignore`, and extensionless files like `Makefile`. The tool's current categorization logic handles compound extensions accidentally well (`.gz` maps to Archives) but fails for files categorized by name rather than extension. A production-quality file organizer would need a secondary categorization pass that checks the full filename against a known-names map (e.g., `Makefile`, `Dockerfile`, `Vagrantfile` → Code) after the extension-based check returns `Other`.

## Testing CLI Tools in Kotlin

Testing CLI tools requires creating temporary directory structures, running the tool's core logic against them, and verifying both the output and the file system state. Kotlin's JUnit integration with the `kotlin.test` library provides the testing framework, and `java.io.File.createTempDir()` (or `kotlin.io.path.createTempDirectory()`) provides isolated test directories.

```kotlin
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import java.io.File

class FileSortTest {

    private fun createTestDirectory(): File {
        val tempDir = File(System.getProperty("java.io.tmpdir"), "filesort-test-${System.nanoTime()}")
        tempDir.mkdirs()

        // Create test files with known extensions and sizes
        File(tempDir, "photo.jpg").writeText("x".repeat(1024))      // 1 KB image
        File(tempDir, "report.pdf").writeText("x".repeat(2048))     // 2 KB document
        File(tempDir, "app.kt").writeText("fun main() {}")          // code file
        File(tempDir, "data.csv").writeText("a,b,c\n1,2,3")        // document
        File(tempDir, "archive.zip").writeText("x".repeat(4096))    // 4 KB archive
        File(tempDir, "unknown.xyz").writeText("mystery")           // other

        return tempDir
    }

    private fun cleanupTestDir(dir: File) {
        dir.walkBottomUp().forEach { it.delete() }
    }

    @Test
    fun testCategoryFromExtension() {
        assertEquals(FileCategory.Images, FileCategory.fromExtension("jpg"))
        assertEquals(FileCategory.Images, FileCategory.fromExtension("PNG"))
        assertEquals(FileCategory.Documents, FileCategory.fromExtension("pdf"))
        assertEquals(FileCategory.Code, FileCategory.fromExtension("kt"))
        assertEquals(FileCategory.Archives, FileCategory.fromExtension("zip"))
        assertEquals(FileCategory.Other, FileCategory.fromExtension("xyz"))
        assertEquals(FileCategory.Other, FileCategory.fromExtension(""))
    }

    @Test
    fun testScanDirectoryFindsAllCategories() {
        val testDir = createTestDirectory()
        try {
            val summaries = scanDirectory(testDir)

            // Should find 4 categories (Images, Documents, Code, Archives, Other)
            assertTrue(summaries.size >= 4, "Expected at least 4 categories, got ${summaries.size}")

            val imagesSummary = summaries.find { it.category == FileCategory.Images }
            assertEquals(1, imagesSummary?.fileCount, "Expected 1 image file")

            val docsSummary = summaries.find { it.category == FileCategory.Documents }
            assertEquals(2, docsSummary?.fileCount, "Expected 2 document files (pdf + csv)")

            val codeSummary = summaries.find { it.category == FileCategory.Code }
            assertEquals(1, codeSummary?.fileCount, "Expected 1 code file")
        } finally {
            cleanupTestDir(testDir)
        }
    }

    @Test
    fun testScanEmptyDirectory() {
        val emptyDir = File(System.getProperty("java.io.tmpdir"), "filesort-empty-${System.nanoTime()}")
        emptyDir.mkdirs()
        try {
            val summaries = scanDirectory(emptyDir)
            assertTrue(summaries.isEmpty(), "Empty directory should produce no summaries")
        } finally {
            cleanupTestDir(emptyDir)
        }
    }

    @Test
    fun testFormatSize() {
        assertEquals("0 B", formatSize(0))
        assertEquals("512 B", formatSize(512))
        assertEquals("1.0 KB", formatSize(1024))
        assertEquals("1.5 MB", formatSize(1_572_864))
        assertEquals("2.0 GB", formatSize(2_147_483_648))
    }

    @Test
    fun testMoveFilesCreatesDirectories() {
        val testDir = createTestDirectory()
        try {
            val summaries = scanDirectory(testDir)
            moveFiles(testDir, summaries)

            // Verify category directories were created
            assertTrue(File(testDir, "images").exists(), "images directory should exist")
            assertTrue(File(testDir, "documents").exists(), "documents directory should exist")
            assertTrue(File(testDir, "code").exists(), "code directory should exist")

            // Verify files were moved
            assertTrue(File(testDir, "images/photo.jpg").exists(), "photo.jpg should be in images/")
            assertTrue(File(testDir, "code/app.kt").exists(), "app.kt should be in code/")
        } finally {
            cleanupTestDir(testDir)
        }
    }
}
```

The test suite validates each layer of the CLI tool independently. The `testCategoryFromExtension` test verifies the sealed class mapping, including case insensitivity and the `Other` fallback for unknown extensions. The `testScanDirectoryFindsAllCategories` test creates a temporary directory with known files and asserts that the scanning function produces correct counts per category. The `testMoveFilesCreatesDirectories` test verifies the end-to-end file movement behavior, checking both that category directories are created and that files appear in the correct locations. Every test uses `try/finally` to clean up temporary directories, preventing test pollution. The `createTestDirectory` helper uses `System.nanoTime()` in the directory name to avoid collisions when tests run in parallel. This testing approach — create known state, execute function, assert results, clean up — is the standard pattern for testing code that interacts with the file system.

## What We Learned

- **Data classes** provide automatic `equals`, `hashCode`, `toString`, and `copy` methods, making them ideal for configuration objects (`CliArgs`) and intermediate data structures (`FileInfo`, `CategorySummary`). They encourage immutable design because the generated methods work correctly only when properties are `val` (read-only), steering developers toward value-based programming.

- **Sealed classes** enforce exhaustive pattern matching — the Kotlin compiler verifies that `when` expressions covering a sealed hierarchy handle every subclass. Adding a new `FileCategory` variant automatically surfaces every location that needs updating, preventing the silent bugs that occur when a switch/case statement misses a new enum value.

- **Kotlin's extension properties** like `File.extension` abstract platform-specific file operations behind concise APIs. The `extension` property handles edge cases (no extension → empty string, multiple dots → last segment) consistently, reducing boilerplate compared to manual `lastIndexOf('.')` logic.

- **Functional collection operations** (`map`, `filter`, `sumOf`, `sortedByDescending`) enable declarative data transformation pipelines that are more readable than imperative loops. Each operation produces a new collection, making the data flow explicit and each intermediate step independently testable. The tradeoff is memory allocation for intermediate lists, which is negligible for the data sizes typical in CLI tools.

## Where to Go Next

- Learn how to structure CLI output with [data classes in Kotlin](/languages/kotlin/data-classes) — the foundation for type-safe domain models
- Add concurrent file processing with [coroutines in Kotlin](/languages/kotlin/coroutines) — scan multiple directories simultaneously
- Extend the tool with [extension functions in Kotlin](/languages/kotlin/extension-functions) — add custom behavior to `File` without subclassing
- Visit the [Kotlin language hub](/languages/kotlin) for more concept guides
- Experiment with Kotlin code in the [Kotlin Playground tool](/tools/kotlin-playground)

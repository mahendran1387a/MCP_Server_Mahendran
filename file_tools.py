"""
File System and Git Operations Module
File management, directory operations, and Git integration
"""
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import shutil


class FileOperations:
    """File system operations"""

    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir).resolve()

    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read file contents"""
        try:
            path = Path(file_path)

            if not path.exists():
                return {'error': f'File not found: {file_path}'}

            # Try to detect encoding
            import chardet
            with open(path, 'rb') as f:
                raw_data = f.read()
                encoding = chardet.detect(raw_data)['encoding'] or 'utf-8'

            with open(path, 'r', encoding=encoding) as f:
                content = f.read()

            return {
                'success': True,
                'file_path': str(path),
                'content': content,
                'size': path.stat().st_size,
                'encoding': encoding,
                'lines': content.count('\n') + 1
            }

        except Exception as e:
            return {'error': str(e)}

    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to file"""
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'success': True,
                'file_path': str(path),
                'size': path.stat().st_size
            }

        except Exception as e:
            return {'error': str(e)}

    def list_directory(self, directory: str = ".",
                      recursive: bool = False,
                      pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        List directory contents

        Args:
            directory: Directory path
            recursive: Whether to list recursively
            pattern: Optional glob pattern (e.g., "*.py")

        Returns:
            Dict with file and directory listings
        """
        try:
            path = Path(directory)

            if not path.exists():
                return {'error': f'Directory not found: {directory}'}

            files = []
            directories = []

            if recursive:
                items = path.rglob(pattern or '*')
            else:
                items = path.glob(pattern or '*')

            for item in items:
                if item.is_file():
                    files.append({
                        'name': item.name,
                        'path': str(item),
                        'size': item.stat().st_size,
                        'extension': item.suffix
                    })
                elif item.is_dir():
                    directories.append({
                        'name': item.name,
                        'path': str(item)
                    })

            return {
                'success': True,
                'directory': str(path),
                'num_files': len(files),
                'num_directories': len(directories),
                'files': files,
                'directories': directories
            }

        except Exception as e:
            return {'error': str(e)}

    def search_files(self, directory: str, pattern: str) -> Dict[str, Any]:
        """
        Search for files matching pattern

        Args:
            directory: Directory to search
            pattern: Glob pattern (e.g., "**/*.py")

        Returns:
            List of matching files
        """
        try:
            path = Path(directory)
            matches = list(path.glob(pattern))

            files = [
                {
                    'name': f.name,
                    'path': str(f),
                    'size': f.stat().st_size if f.is_file() else 0
                }
                for f in matches if f.is_file()
            ]

            return {
                'success': True,
                'pattern': pattern,
                'num_matches': len(files),
                'files': files
            }

        except Exception as e:
            return {'error': str(e)}

    def copy_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Copy file"""
        try:
            src = Path(source)
            dst = Path(destination)

            if not src.exists():
                return {'error': f'Source not found: {source}'}

            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

            return {
                'success': True,
                'source': str(src),
                'destination': str(dst),
                'size': dst.stat().st_size
            }

        except Exception as e:
            return {'error': str(e)}

    def move_file(self, source: str, destination: str) -> Dict[str, Any]:
        """Move file"""
        try:
            src = Path(source)
            dst = Path(destination)

            if not src.exists():
                return {'error': f'Source not found: {source}'}

            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))

            return {
                'success': True,
                'source': str(src),
                'destination': str(dst)
            }

        except Exception as e:
            return {'error': str(e)}

    def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete file"""
        try:
            path = Path(file_path)

            if not path.exists():
                return {'error': f'File not found: {file_path}'}

            path.unlink()

            return {
                'success': True,
                'file_path': str(path),
                'deleted': True
            }

        except Exception as e:
            return {'error': str(e)}


class GitOperations:
    """Git repository operations"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.repo = None

    def initialize(self) -> Dict[str, Any]:
        """Initialize Git operations"""
        try:
            from git import Repo

            if (self.repo_path / '.git').exists():
                self.repo = Repo(self.repo_path)
                return {
                    'success': True,
                    'is_repo': True,
                    'branch': self.repo.active_branch.name
                }
            else:
                return {
                    'success': True,
                    'is_repo': False,
                    'message': 'Not a git repository'
                }

        except Exception as e:
            return {'error': str(e)}

    def get_status(self) -> Dict[str, Any]:
        """Get git status"""
        if not self.repo:
            return {'error': 'Not initialized or not a git repo'}

        try:
            return {
                'branch': self.repo.active_branch.name,
                'is_dirty': self.repo.is_dirty(),
                'untracked_files': self.repo.untracked_files,
                'modified_files': [item.a_path for item in self.repo.index.diff(None)],
                'staged_files': [item.a_path for item in self.repo.index.diff('HEAD')]
            }

        except Exception as e:
            return {'error': str(e)}

    def get_log(self, max_count: int = 10) -> Dict[str, Any]:
        """Get git log"""
        if not self.repo:
            return {'error': 'Not initialized or not a git repo'}

        try:
            commits = []
            for commit in list(self.repo.iter_commits(max_count=max_count)):
                commits.append({
                    'hash': commit.hexsha[:8],
                    'author': str(commit.author),
                    'date': commit.committed_datetime.isoformat(),
                    'message': commit.message.strip()
                })

            return {
                'num_commits': len(commits),
                'commits': commits
            }

        except Exception as e:
            return {'error': str(e)}

    def get_diff(self) -> Dict[str, Any]:
        """Get current diff"""
        if not self.repo:
            return {'error': 'Not initialized or not a git repo'}

        try:
            diff = self.repo.git.diff()

            return {
                'has_changes': bool(diff),
                'diff': diff
            }

        except Exception as e:
            return {'error': str(e)}

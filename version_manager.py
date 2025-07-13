#!/usr/bin/env python3
"""
Sales Agent Commission - Version Manager
Manages version updates across all files and generates release documentation.
"""

import os
import re
import json
import argparse
from datetime import datetime
from pathlib import Path

class VersionManager:
    def __init__(self):
        self.app_root = Path(".")
        self.version_files = [
            "sales_agent_commission/__init__.py",
            "sales_agent_commission/sales_agent_commission/__init__.py",
            "setup.py",
            "VERSION"
        ]
    
    def get_current_version(self):
        """Get current version from VERSION file"""
        version_file = self.app_root / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        return "1.0.0"
    
    def update_version(self, new_version):
        """Update version in all relevant files"""
        print(f"🔄 Updating version to {new_version}")
        
        # Update VERSION file
        version_file = self.app_root / "VERSION"
        version_file.write_text(new_version)
        print(f"✅ Updated: {version_file}")
        
        # Update __init__.py files
        for file_path in ["sales_agent_commission/__init__.py", "sales_agent_commission/sales_agent_commission/__init__.py"]:
            full_path = self.app_root / file_path
            if full_path.exists():
                content = full_path.read_text()
                updated_content = re.sub(
                    r'__version__ = ["\'].*["\']',
                    f'__version__ = \'{new_version}\'',
                    content
                )
                full_path.write_text(updated_content)
                print(f"✅ Updated: {full_path}")
        
        # Update setup.py version import (it reads from __init__.py)
        print(f"✅ Setup.py will automatically use version from __init__.py")
        
        print(f"🎉 Version updated to {new_version} successfully!")
    
    def generate_changelog_entry(self, version, changes):
        """Generate changelog entry for new version"""
        date = datetime.now().strftime("%Y-%m-%d")
        
        entry = f"""
## [{version}] - {date}

### 🚀 Added
{self._format_changes(changes.get('added', []))}

### 🔧 Fixed
{self._format_changes(changes.get('fixed', []))}

### 🔄 Changed
{self._format_changes(changes.get('changed', []))}

### 📈 Improved
{self._format_changes(changes.get('improved', []))}

### 🛠️ Technical
{self._format_changes(changes.get('technical', []))}

### 🗑️ Removed
{self._format_changes(changes.get('removed', []))}

---
"""
        return entry
    
    def _format_changes(self, changes):
        """Format changes list"""
        if not changes:
            return "- No changes in this category"
        
        formatted = []
        for change in changes:
            formatted.append(f"- {change}")
        return "\n".join(formatted)
    
    def update_changelog(self, version, changes):
        """Update CHANGELOG.md with new version"""
        changelog_file = self.app_root / "CHANGELOG.md"
        
        if not changelog_file.exists():
            print("❌ CHANGELOG.md not found!")
            return
        
        content = changelog_file.read_text()
        
        # Find insertion point (after the header)
        header_end = content.find("## [")
        if header_end == -1:
            print("❌ Could not find insertion point in CHANGELOG.md")
            return
        
        # Generate new entry
        new_entry = self.generate_changelog_entry(version, changes)
        
        # Insert new entry
        updated_content = content[:header_end] + new_entry + content[header_end:]
        
        changelog_file.write_text(updated_content)
        print(f"✅ Updated: {changelog_file}")
    
    def create_release_notes(self, version, changes):
        """Create release notes file"""
        date = datetime.now().strftime("%B %d, %Y")
        
        template = f"""# 🚀 Sales Agent Commission v{version} Release Notes

**Release Date**: {date}  
**Version**: {version}  
**Type**: Feature Release  
**Compatibility**: ERPNext v13.0+, Frappe Framework v13.0+

---

## 🎯 **Release Summary**

This release includes the following changes:

### 🚀 **New Features**
{self._format_changes(changes.get('added', []))}

### 🔧 **Bug Fixes**
{self._format_changes(changes.get('fixed', []))}

### 🔄 **Changes**
{self._format_changes(changes.get('changed', []))}

### 📈 **Improvements**
{self._format_changes(changes.get('improved', []))}

### 🛠️ **Technical Updates**
{self._format_changes(changes.get('technical', []))}

### 🗑️ **Removed**
{self._format_changes(changes.get('removed', []))}

## 🚀 **Installation**

### **New Installation**
```bash
# Install the app
bench --site your-site install-app sales_agent_commission

# Migrate database
bench --site your-site migrate

# Restart services
bench restart
```

### **Upgrade from Previous Version**
```bash
# Update app
bench --site your-site migrate

# Restart services
bench restart
```

## 📋 **Verification**

After installation/upgrade, verify:
- [ ] App version shows as {version}
- [ ] All doctypes are accessible
- [ ] No console errors
- [ ] Features work as expected

## 🆘 **Support**

For issues or questions:
- **Documentation**: Check installation and troubleshooting guides
- **GitHub Issues**: Report bugs and feature requests
- **Community**: Join discussions and get help

---

**Thank you for using Sales Agent Commission Management System!**
"""
        
        release_file = self.app_root / f"RELEASE_NOTES_v{version}.md"
        release_file.write_text(template)
        print(f"✅ Created: {release_file}")
    
    def validate_version(self, version):
        """Validate version format (semantic versioning)"""
        pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$'
        return re.match(pattern, version) is not None
    
    def get_version_info(self):
        """Get current version information"""
        current = self.get_current_version()
        print(f"📋 Current Version: {current}")
        
        # Parse version parts
        parts = current.split('.')
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
        
        # Suggest next versions
        print(f"🔄 Suggested next versions:")
        print(f"   Patch: {major}.{minor}.{patch + 1}")
        print(f"   Minor: {major}.{minor + 1}.0")
        print(f"   Major: {major + 1}.0.0")
    
    def create_git_tag(self, version):
        """Create git tag for version (if git is available)"""
        try:
            import subprocess
            
            # Create tag
            subprocess.run(['git', 'tag', f'v{version}'], check=True)
            print(f"✅ Created git tag: v{version}")
            
            # Push tag
            subprocess.run(['git', 'push', 'origin', f'v{version}'], check=True)
            print(f"✅ Pushed git tag: v{version}")
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ Git not available or error creating tag")

def main():
    parser = argparse.ArgumentParser(description="Sales Agent Commission Version Manager")
    parser.add_argument('--version', help='New version number (e.g., 1.2.0)')
    parser.add_argument('--info', action='store_true', help='Show current version info')
    parser.add_argument('--changelog', help='Path to changes JSON file')
    parser.add_argument('--tag', action='store_true', help='Create git tag')
    
    args = parser.parse_args()
    
    vm = VersionManager()
    
    if args.info:
        vm.get_version_info()
        return
    
    if not args.version:
        print("❌ Please provide a version number with --version")
        vm.get_version_info()
        return
    
    if not vm.validate_version(args.version):
        print("❌ Invalid version format. Use semantic versioning (e.g., 1.2.0)")
        return
    
    # Load changes if provided
    changes = {}
    if args.changelog:
        try:
            with open(args.changelog, 'r') as f:
                changes = json.load(f)
        except FileNotFoundError:
            print(f"❌ Changes file not found: {args.changelog}")
            return
    
    # Update version
    vm.update_version(args.version)
    
    # Update changelog if changes provided
    if changes:
        vm.update_changelog(args.version, changes)
        vm.create_release_notes(args.version, changes)
    
    # Create git tag if requested
    if args.tag:
        vm.create_git_tag(args.version)
    
    print(f"🎉 Version {args.version} release preparation complete!")

if __name__ == "__main__":
    main()
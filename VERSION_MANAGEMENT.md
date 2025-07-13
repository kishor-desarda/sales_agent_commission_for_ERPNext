# Version Management Guide

This guide explains how to manage versions and releases for the Sales Agent Commission app using professional software development practices.

## 📋 **Current Version System**

The app follows [Semantic Versioning](https://semver.org/) (SemVer):
- **Major** (X.0.0): Breaking changes, significant new features
- **Minor** (1.X.0): New features, backward compatible
- **Patch** (1.1.X): Bug fixes, small improvements

**Current Version**: `1.1.0`

## 🛠️ **Version Manager Tool**

The `version_manager.py` script automates version updates across all files and generates release documentation.

### **Check Current Version**
```bash
python3 version_manager.py --info
```

### **Update Version**
```bash
# Update to new version
python3 version_manager.py --version 1.2.0

# Update with changelog
python3 version_manager.py --version 1.2.0 --changelog changes.json

# Update with git tag
python3 version_manager.py --version 1.2.0 --changelog changes.json --tag
```

## 📝 **Release Process**

### **1. Prepare Changes**
Create a `changes.json` file with your changes:
```json
{
  "added": [
    "New feature: Enhanced dashboard",
    "New report: Performance analytics"
  ],
  "fixed": [
    "Fixed commission calculation bug",
    "Fixed mobile view issue"
  ],
  "changed": [
    "Updated UI layout",
    "Changed default settings"
  ],
  "improved": [
    "Better performance",
    "Enhanced error handling"
  ],
  "technical": [
    "Upgraded dependencies",
    "Added unit tests"
  ],
  "removed": [
    "Removed deprecated features"
  ]
}
```

### **2. Update Version**
```bash
# For bug fixes (patch)
python3 version_manager.py --version 1.1.1 --changelog changes.json

# For new features (minor)
python3 version_manager.py --version 1.2.0 --changelog changes.json

# For breaking changes (major)
python3 version_manager.py --version 2.0.0 --changelog changes.json
```

### **3. Files Updated Automatically**
- `VERSION` - Main version file
- `sales_agent_commission/__init__.py` - App version
- `sales_agent_commission/sales_agent_commission/__init__.py` - Module version
- `setup.py` - Package version (reads from __init__.py)
- `CHANGELOG.md` - Updated with new entry
- `RELEASE_NOTES_vX.X.X.md` - New release notes created

### **4. Create Git Tag (Optional)**
```bash
python3 version_manager.py --version 1.2.0 --changelog changes.json --tag
```

## 📚 **Documentation Updates**

### **Automatic Updates**
- **CHANGELOG.md**: Updated with structured changes
- **Release Notes**: Individual files for each version
- **Version Files**: All version references updated

### **Manual Updates**
- **README.md**: Update installation instructions if needed
- **Documentation**: Update any version-specific references
- **Installation Guides**: Update compatibility information

## 🔄 **Version History**

### **v1.1.0** (Current)
- **Type**: Major Feature Release
- **Date**: January 15, 2024
- **Highlights**: 
  - Complete agent master redesign
  - Payment reconciliation logic
  - Installation issues resolved
  - Sales Partner integration

### **v1.0.0** (Initial)
- **Type**: Initial Release
- **Date**: January 1, 2024
- **Highlights**: 
  - Basic commission management
  - Simple agent rules
  - Payment vouchers

## 🎯 **Version Planning**

### **v1.2.0** (Planned)
- **Type**: Minor Feature Release
- **Target**: Q2 2024
- **Focus**: 
  - Enhanced reporting
  - Mobile optimization
  - Performance improvements

### **v1.3.0** (Planned)
- **Type**: Minor Feature Release
- **Target**: Q3 2024
- **Focus**: 
  - Advanced analytics
  - Integration improvements
  - Workflow enhancements

### **v2.0.0** (Future)
- **Type**: Major Release
- **Target**: Q4 2024
- **Focus**: 
  - ERPNext v14 compatibility
  - Architecture improvements
  - Breaking changes for better design

## 🚀 **Release Guidelines**

### **When to Increment**

#### **Patch (1.1.X)**
- Bug fixes
- Security patches
- Documentation updates
- Performance improvements (no API changes)

#### **Minor (1.X.0)**
- New features (backward compatible)
- New doctypes or fields
- Enhanced functionality
- New integrations

#### **Major (X.0.0)**
- Breaking changes
- Removed features
- Changed APIs
- Architecture changes
- Framework version upgrades

### **Pre-Release Process**

1. **Development**: Feature development in branches
2. **Testing**: Comprehensive testing in development environment
3. **Documentation**: Update all relevant documentation
4. **Version Update**: Use version manager to update version
5. **Release**: Create release and distribute

### **Post-Release Process**

1. **Verification**: Verify installation on clean environment
2. **Documentation**: Update installation guides if needed
3. **Support**: Monitor for issues and provide support
4. **Feedback**: Collect feedback for next release

## 📋 **Checklist for Releases**

### **Pre-Release**
- [ ] All features tested and working
- [ ] Documentation updated
- [ ] Changes documented in changes.json
- [ ] Version number decided (semantic versioning)
- [ ] Installation tested on clean environment

### **Release**
- [ ] Run version manager with new version
- [ ] Verify all files updated correctly
- [ ] Create git tag if using version control
- [ ] Update any external documentation
- [ ] Prepare release announcement

### **Post-Release**
- [ ] Monitor for installation issues
- [ ] Update any related documentation
- [ ] Respond to user feedback
- [ ] Plan next release based on feedback

## 🛠️ **Tools and Scripts**

### **Version Manager** (`version_manager.py`)
- Automated version updates
- Changelog generation
- Release notes creation
- Git tag creation

### **Installation Fixer** (`fix_installation.py`)
- Resolves installation issues
- Creates missing files
- Verifies app structure

### **Templates**
- `changes_template.json`: Template for tracking changes
- Release note templates
- Changelog format

## 📞 **Support**

For version management questions:
- Check this guide first
- Review existing changelog and release notes
- Follow semantic versioning principles
- Test thoroughly before releasing

---

**Remember**: Good version management is crucial for maintaining a professional, reliable software product. Always test thoroughly and document changes comprehensively.
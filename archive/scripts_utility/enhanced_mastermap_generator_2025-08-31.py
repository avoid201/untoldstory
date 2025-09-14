#!/usr/bin/env python3
"""
Enhanced Mastermap Generator für Untold Story
Optimiert für AI-Lesbarkeit und strukturierte Übersichtlichkeit
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import json
import re

@dataclass
class EnhancedFunctionInfo:
    """Erweiterte Informationen über eine Funktion."""
    name: str
    args: List[str]
    decorators: List[str]
    docstring: Optional[str]
    line_number: int
    complexity_score: int  # Basierend auf Anzahl der Statements
    return_type: Optional[str]
    is_async: bool = False
    is_property: bool = False
    is_staticmethod: bool = False
    is_classmethod: bool = False
    is_public: bool = True
    
    def __post_init__(self):
        self.is_public = not self.name.startswith('_')

@dataclass 
class EnhancedClassInfo:
    """Erweiterte Informationen über eine Klasse."""
    name: str
    bases: List[str]
    decorators: List[str]
    docstring: Optional[str]
    line_number: int
    methods: List[EnhancedFunctionInfo] = field(default_factory=list)
    properties: List[EnhancedFunctionInfo] = field(default_factory=list)
    class_variables: List[str] = field(default_factory=list)
    is_abstract: bool = False
    is_dataclass: bool = False
    is_enum: bool = False
    complexity_score: int = 0
    
    def __post_init__(self):
        self.is_abstract = 'ABC' in self.bases or any('abstract' in d.lower() for d in self.decorators)
        self.is_dataclass = 'dataclass' in self.decorators
        self.is_enum = 'Enum' in self.bases or 'IntEnum' in self.bases
        self.complexity_score = len(self.methods) + len(self.properties)

@dataclass
class EnhancedImportInfo:
    """Erweiterte Informationen über ein Import."""
    module: str
    names: List[str]  
    alias: Optional[str] = None
    is_from_import: bool = False
    import_level: str = "external"  # local, engine, external, stdlib
    line_number: int = 0

@dataclass
class EnhancedFileInfo:
    """Erweiterte Informationen über eine Python-Datei."""
    path: str
    relative_path: str
    line_count: int
    module_category: str  # core, systems, ui, scenes, world, graphics, audio, devtools
    importance_level: int  # 1=critical, 2=important, 3=supporting, 4=utility
    imports: List[EnhancedImportInfo] = field(default_factory=list)
    classes: List[EnhancedClassInfo] = field(default_factory=list)
    functions: List[EnhancedFunctionInfo] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)
    docstring: Optional[str] = None
    key_patterns: List[str] = field(default_factory=list)  # Design patterns used
    dependencies: List[str] = field(default_factory=list)  # Files this depends on
    dependents: List[str] = field(default_factory=list)    # Files that depend on this

class EnhancedCodeAnalyzer(ast.NodeVisitor):
    """Erweiterte AST Visitor mit AI-optimierten Metadaten."""
    
    def __init__(self):
        self.imports: List[EnhancedImportInfo] = []
        self.classes: List[EnhancedClassInfo] = []
        self.functions: List[EnhancedFunctionInfo] = []
        self.constants: List[str] = []
        self.current_class: Optional[EnhancedClassInfo] = None
        self.complexity_counter = 0
        
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Berechnet die zyklomatische Komplexität."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
        
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extrahiert Return-Type-Annotation falls vorhanden."""
        if node.returns:
            try:
                return ast.unparse(node.returns)
            except:
                return None
        return None
        
    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            import_level = self._classify_import(alias.name)
            import_info = EnhancedImportInfo(
                module=alias.name,
                names=[],
                alias=alias.asname,
                is_from_import=False,
                import_level=import_level,
                line_number=node.lineno
            )
            self.imports.append(import_info)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            names = [alias.name for alias in node.names]
            import_level = self._classify_import(node.module)
            import_info = EnhancedImportInfo(
                module=node.module,
                names=names,
                is_from_import=True,
                import_level=import_level,
                line_number=node.lineno
            )
            self.imports.append(import_info)
        self.generic_visit(node)
    
    def _classify_import(self, module_name: str) -> str:
        """Klassifiziert Import-Level."""
        if module_name.startswith('engine.'):
            return 'engine'
        elif module_name in ['typing', 'dataclasses', 'enum', 'pathlib', 'os', 'sys', 'json', 're', 'time', 'logging', 'collections']:
            return 'stdlib'
        elif module_name in ['pygame', 'numpy', 'PIL']:
            return 'external'
        else:
            return 'external'
        
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(ast.unparse(base))
                
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            else:
                decorators.append(ast.unparse(decorator))
                
        docstring = ast.get_docstring(node)
        
        class_info = EnhancedClassInfo(
            name=node.name,
            bases=bases,
            decorators=decorators,
            docstring=docstring,
            line_number=node.lineno
        )
        
        # Sammle Klassen-Level Variablen
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        class_info.class_variables.append(target.id)
        
        old_class = self.current_class
        self.current_class = class_info
        self.classes.append(class_info)
        
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        args = [arg.arg for arg in node.args.args]
        
        decorators = []
        is_property = False
        is_staticmethod = False
        is_classmethod = False
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                dec_name = decorator.id
                decorators.append(dec_name)
                if dec_name == 'property':
                    is_property = True
                elif dec_name == 'staticmethod':
                    is_staticmethod = True
                elif dec_name == 'classmethod':
                    is_classmethod = True
            else:
                decorators.append(ast.unparse(decorator))
                
        docstring = ast.get_docstring(node)
        complexity = self._calculate_complexity(node)
        return_type = self._extract_return_type(node)
        
        func_info = EnhancedFunctionInfo(
            name=node.name,
            args=args,
            decorators=decorators,
            docstring=docstring,
            line_number=node.lineno,
            complexity_score=complexity,
            return_type=return_type,
            is_async=False,
            is_property=is_property,
            is_staticmethod=is_staticmethod,
            is_classmethod=is_classmethod
        )
        
        if self.current_class:
            if is_property:
                self.current_class.properties.append(func_info)
            else:
                self.current_class.methods.append(func_info)
        else:
            self.functions.append(func_info)
            
        self.generic_visit(node)
        
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        args = [arg.arg for arg in node.args.args]
        
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            else:
                decorators.append(ast.unparse(decorator))
                
        docstring = ast.get_docstring(node)
        complexity = self._calculate_complexity(node)
        return_type = self._extract_return_type(node)
        
        func_info = EnhancedFunctionInfo(
            name=node.name,
            args=args,
            decorators=decorators,
            docstring=docstring,
            line_number=node.lineno,
            complexity_score=complexity,
            return_type=return_type,
            is_async=True
        )
        
        if self.current_class:
            self.current_class.methods.append(func_info)
        else:
            self.functions.append(func_info)
            
        self.generic_visit(node)
        
    def visit_Assign(self, node: ast.Assign) -> None:
        if not self.current_class:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    self.constants.append(target.id)
        self.generic_visit(node)

class EnhancedMastermapGenerator:
    """Erweiterte Mastermap-Generierung mit AI-Optimierungen."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.engine_path = self.project_root / "engine"
        self.files: Dict[str, EnhancedFileInfo] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        
        # AI-freundliche Kategorisierung
        self.module_categories = {
            'core': {'importance': 1, 'description': 'Foundation systems'},
            'systems': {'importance': 1, 'description': 'Core gameplay mechanics'},
            'scenes': {'importance': 2, 'description': 'Scene management'},
            'ui': {'importance': 2, 'description': 'User interface'},
            'world': {'importance': 2, 'description': 'Game world systems'},
            'graphics': {'importance': 3, 'description': 'Rendering and graphics'},
            'audio': {'importance': 3, 'description': 'Audio systems'},
            'devtools': {'importance': 4, 'description': 'Development tools'}
        }
        
    def _categorize_file(self, file_path: Path) -> Tuple[str, int]:
        """Kategorisiert Datei und bestimmt Wichtigkeitslevel."""
        path_parts = file_path.parts
        if len(path_parts) >= 2:
            category = path_parts[1]  # engine/[category]/...
            if category in self.module_categories:
                return category, self.module_categories[category]['importance']
        return 'misc', 4
        
    def _detect_patterns(self, file_info: EnhancedFileInfo) -> List[str]:
        """Erkennt Design Patterns in der Datei."""
        patterns = []
        
        # Singleton Pattern
        for cls in file_info.classes:
            if any('_instance' in var for var in cls.class_variables):
                patterns.append('Singleton')
                
        # Factory Pattern
        if any('factory' in cls.name.lower() or 'Factory' in cls.name for cls in file_info.classes):
            patterns.append('Factory')
            
        # Observer Pattern
        if any('observer' in cls.name.lower() or 'Observer' in cls.name for cls in file_info.classes):
            patterns.append('Observer')
            
        # Manager Pattern
        if any('manager' in cls.name.lower() or 'Manager' in cls.name for cls in file_info.classes):
            patterns.append('Manager')
            
        return patterns
    
    def _build_dependency_graph(self) -> None:
        """Baut Dependency-Graph für Cross-Referencing."""
        for file_path, file_info in self.files.items():
            for import_info in file_info.imports:
                if import_info.import_level == 'engine':
                    # Konvertiere import zu Dateipfad
                    import_path = import_info.module.replace('.', '/') + '.py'
                    if import_path.startswith('engine/'):
                        import_path = import_path[7:]  # Remove 'engine/' prefix
                    
                    file_info.dependencies.append(import_path)
                    self.dependency_graph[file_path].add(import_path)
                    
                    # Umgekehrte Dependencies
                    if import_path in self.files:
                        self.files[import_path].dependents.append(file_path)
    
    def analyze_file(self, file_path: Path) -> Optional[EnhancedFileInfo]:
        """Analysiert eine einzelne Python-Datei mit erweiterten Metadaten."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            analyzer = EnhancedCodeAnalyzer()
            analyzer.visit(tree)
            
            line_count = len(content.splitlines())
            docstring = ast.get_docstring(tree)
            relative_path = str(file_path.relative_to(self.project_root))
            
            category, importance = self._categorize_file(file_path.relative_to(self.project_root))
            
            file_info = EnhancedFileInfo(
                path=str(file_path),
                relative_path=relative_path,
                line_count=line_count,
                module_category=category,
                importance_level=importance,
                imports=analyzer.imports,
                classes=analyzer.classes,
                functions=analyzer.functions,
                constants=analyzer.constants,
                docstring=docstring
            )
            
            file_info.key_patterns = self._detect_patterns(file_info)
            
            return file_info
            
        except Exception as e:
            print(f"Fehler beim Analysieren von {file_path}: {e}")
            return None
    
    def scan_directory(self) -> None:
        """Scannt das engine/ Verzeichnis nach Python-Dateien."""
        if not self.engine_path.exists():
            raise FileNotFoundError(f"Engine-Pfad nicht gefunden: {self.engine_path}")
            
        for py_file in self.engine_path.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
                
            file_info = self.analyze_file(py_file)
            if file_info:
                self.files[file_info.relative_path] = file_info
                
        # Nach dem Scannen: Dependency-Graph aufbauen
        self._build_dependency_graph()
    
    def generate_ai_optimized_markdown(self) -> str:
        """Generiert AI-optimierten Markdown-Report."""
        markdown = []
        
        # Header mit Metadaten
        markdown.append("# 🤖 AI-Optimized Untold Story Mastermap")
        markdown.append("")
        markdown.append("<!-- AI_PARSING_METADATA")
        markdown.append(f"PROJECT: Untold Story")
        markdown.append(f"LANGUAGE: Python")
        markdown.append(f"FRAMEWORK: pygame-ce")
        markdown.append(f"ARCHITECTURE: Modular RPG Engine")
        markdown.append(f"FILES: {len(self.files)}")
        markdown.append(f"TOTAL_LINES: {sum(f.line_count for f in self.files.values())}")
        markdown.append(f"TOTAL_CLASSES: {sum(len(f.classes) for f in self.files.values())}")
        markdown.append("-->")
        markdown.append("")
        
        # Quick Reference für AIs
        markdown.append("## 🎯 AI Quick Reference")
        markdown.append("")
        markdown.append("### 🔥 Critical Systems (Priority 1)")
        critical_files = [f for f in self.files.values() if f.importance_level == 1]
        markdown.append(f"- **{len(critical_files)} files** - Foundation & Core Gameplay")
        
        for category in ['core', 'systems']:
            cat_files = [f for f in critical_files if f.module_category == category]
            if cat_files:
                total_classes = sum(len(f.classes) for f in cat_files)
                total_lines = sum(f.line_count for f in cat_files)
                markdown.append(f"  - `{category}/`: {len(cat_files)} files, {total_classes} classes, {total_lines:,} LOC")
        
        markdown.append("")
        markdown.append("### 🎮 Key Components")
        
        # Battle System Highlight
        battle_files = [f for f in self.files.values() if 'battle' in f.relative_path]
        battle_classes = sum(len(f.classes) for f in battle_files)
        battle_lines = sum(f.line_count for f in battle_files)
        markdown.append(f"- **Battle System**: {len(battle_files)} files, {battle_classes} classes, {battle_lines:,} LOC")
        
        # World System
        world_files = [f for f in self.files.values() if f.module_category == 'world']
        world_classes = sum(len(f.classes) for f in world_files)
        world_lines = sum(f.line_count for f in world_files)
        markdown.append(f"- **World System**: {len(world_files)} files, {world_classes} classes, {world_lines:,} LOC")
        
        # UI System
        ui_files = [f for f in self.files.values() if f.module_category == 'ui']
        ui_classes = sum(len(f.classes) for f in ui_files)
        ui_lines = sum(f.line_count for f in ui_files)
        markdown.append(f"- **UI System**: {len(ui_files)} files, {ui_classes} classes, {ui_lines:,} LOC")
        
        markdown.append("")
        
        # Design Patterns Overview
        all_patterns = []
        for file_info in self.files.values():
            all_patterns.extend(file_info.key_patterns)
        pattern_count = Counter(all_patterns)
        
        markdown.append("### 🏗️ Design Patterns Detected")
        for pattern, count in pattern_count.most_common():
            markdown.append(f"- **{pattern}**: {count} implementations")
        markdown.append("")
        
        # Kategorisierte Datei-Übersicht
        markdown.append("## 📊 Hierarchical System Overview")
        markdown.append("")
        
        # Nach Kategorien gruppiert
        by_category = defaultdict(list)
        for file_info in self.files.values():
            by_category[file_info.module_category].append(file_info)
        
        for category in ['core', 'systems', 'scenes', 'ui', 'world', 'graphics', 'audio', 'devtools']:
            if category not in by_category:
                continue
                
            files = sorted(by_category[category], key=lambda x: (-len(x.classes), -x.line_count, x.relative_path))
            
            total_classes = sum(len(f.classes) for f in files)
            total_methods = sum(sum(len(c.methods) for c in f.classes) for f in files)
            total_lines = sum(f.line_count for f in files)
            importance = self.module_categories.get(category, {}).get('importance', 4)
            
            priority_icon = "🔥" if importance == 1 else "⭐" if importance == 2 else "📦" if importance == 3 else "🔧"
            
            markdown.append(f"### {priority_icon} {category.title()} System")
            markdown.append("")
            markdown.append(f"**Overview:** {len(files)} files, {total_classes} classes, {total_methods} methods, {total_lines:,} LOC")
            markdown.append("")
            
            # Tabelle der wichtigsten Dateien
            markdown.append("| File | Classes | Methods | LOC | Key Features |")
            markdown.append("|------|---------|---------|-----|--------------|")
            
            for file_info in files[:10]:  # Top 10 files per category
                filename = Path(file_info.relative_path).name
                class_count = len(file_info.classes)
                method_count = sum(len(c.methods) for c in file_info.classes)
                
                # Extrahiere wichtigste Klassen
                key_classes = [c.name for c in file_info.classes[:3]]
                key_features = ", ".join(key_classes) if key_classes else "Functions"
                if len(key_features) > 40:
                    key_features = key_features[:37] + "..."
                
                markdown.append(f"| `{filename}` | {class_count} | {method_count} | {file_info.line_count} | {key_features} |")
            
            if len(files) > 10:
                markdown.append(f"| ... | ... | ... | ... | +{len(files)-10} more files |")
            
            markdown.append("")
        
        # Class Reference Index
        markdown.append("## 🗂️ Complete Class Reference")
        markdown.append("")
        
        all_classes = []
        for file_info in self.files.values():
            for class_info in file_info.classes:
                all_classes.append((file_info, class_info))
        
        # Sortiere nach Komplexität/Wichtigkeit
        all_classes.sort(key=lambda x: (-x[1].complexity_score, -len(x[1].methods), x[1].name))
        
        markdown.append("### 🏆 Most Complex Classes")
        markdown.append("")
        markdown.append("| Class | File | Methods | Properties | Complexity | Type |")
        markdown.append("|-------|------|---------|------------|------------|------|")
        
        for file_info, class_info in all_classes[:20]:  # Top 20 most complex
            filename = Path(file_info.relative_path).name
            class_type = "🔧Enum" if class_info.is_enum else "📋Data" if class_info.is_dataclass else "🏭Abstract" if class_info.is_abstract else "📦Class"
            
            markdown.append(f"| `{class_info.name}` | `{filename}` | {len(class_info.methods)} | {len(class_info.properties)} | {class_info.complexity_score} | {class_type} |")
        
        markdown.append("")
        
        # Import Dependencies
        markdown.append("## 🔗 Dependency Analysis")
        markdown.append("")
        
        # Most imported modules
        import_counter = Counter()
        for file_info in self.files.values():
            for import_info in file_info.imports:
                if import_info.import_level == 'engine':
                    import_counter[import_info.module] += 1
        
        markdown.append("### 📥 Most Imported Engine Modules")
        markdown.append("")
        for module, count in import_counter.most_common(10):
            markdown.append(f"- `{module}`: imported by {count} files")
        markdown.append("")
        
        # Files with most dependencies
        dependency_count = [(len(f.dependencies), f) for f in self.files.values()]
        dependency_count.sort(reverse=True)
        
        markdown.append("### 📊 Files with Most Dependencies")
        markdown.append("")
        for dep_count, file_info in dependency_count[:10]:
            filename = Path(file_info.relative_path).name
            markdown.append(f"- `{filename}`: {dep_count} dependencies")
        
        markdown.append("")
        
        # AI Parsing Tags
        markdown.append("<!-- AI_PARSING_TAGS")
        for category, files in by_category.items():
            for file_info in files:
                for class_info in file_info.classes:
                    markdown.append(f"CLASS:{class_info.name}|FILE:{file_info.relative_path}|CATEGORY:{category}")
        markdown.append("-->")
        
        return "\n".join(markdown)

def main():
    """Hauptfunktion."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."
    
    print(f"🚀 Enhanced Mastermap Analysis: {project_root}")
    
    try:
        generator = EnhancedMastermapGenerator(project_root)
        generator.scan_directory()
        
        print(f"✅ {len(generator.files)} files analyzed with enhanced metadata")
        
        # Statistiken ausgeben
        total_classes = sum(len(f.classes) for f in generator.files.values())
        total_lines = sum(f.line_count for f in generator.files.values())
        total_methods = sum(sum(len(c.methods) for c in f.classes) for f in generator.files.values())
        
        print(f"📊 Enhanced Stats: {len(generator.files)} files, {total_lines:,} lines, {total_classes} classes, {total_methods} methods")
        
        # Enhanced Markdown-Report generieren
        enhanced_report = generator.generate_ai_optimized_markdown()
        
        # Report speichern
        output_path = Path(project_root) / "AI_OPTIMIZED_MASTERMAP.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(enhanced_report)
        
        print(f"🤖 AI-Optimized Mastermap saved: {output_path}")
        
        return enhanced_report, generator
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

if __name__ == "__main__":
    main()

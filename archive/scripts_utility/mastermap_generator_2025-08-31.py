#!/usr/bin/env python3
"""
Mastermap Generator für Untold Story
Extrahiert automatisch alle Imports, Klassen und Funktionen aus dem Code
für eine vollständige und akkurate Dokumentation.
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import json

@dataclass
class FunctionInfo:
    """Informationen über eine Funktion."""
    name: str
    args: List[str]
    decorators: List[str]
    docstring: Optional[str]
    line_number: int
    is_async: bool = False
    is_property: bool = False
    is_staticmethod: bool = False
    is_classmethod: bool = False

@dataclass 
class ClassInfo:
    """Informationen über eine Klasse."""
    name: str
    bases: List[str]
    decorators: List[str]
    docstring: Optional[str]
    line_number: int
    methods: List[FunctionInfo] = field(default_factory=list)
    properties: List[FunctionInfo] = field(default_factory=list)
    class_variables: List[str] = field(default_factory=list)

@dataclass
class ImportInfo:
    """Informationen über ein Import."""
    module: str
    names: List[str]  # Für "from X import Y, Z"
    alias: Optional[str] = None  # Für "import X as Y"
    is_from_import: bool = False

@dataclass
class FileInfo:
    """Informationen über eine Python-Datei."""
    path: str
    relative_path: str
    line_count: int
    imports: List[ImportInfo] = field(default_factory=list)
    classes: List[ClassInfo] = field(default_factory=list)
    functions: List[FunctionInfo] = field(default_factory=list)
    constants: List[str] = field(default_factory=list)
    docstring: Optional[str] = None

class CodeAnalyzer(ast.NodeVisitor):
    """AST Visitor zum Extrahieren von Code-Informationen."""
    
    def __init__(self):
        self.imports: List[ImportInfo] = []
        self.classes: List[ClassInfo] = []
        self.functions: List[FunctionInfo] = []
        self.constants: List[str] = []
        self.current_class: Optional[ClassInfo] = None
        
    def visit_Import(self, node: ast.Import) -> None:
        """Besuche import statements."""
        for alias in node.names:
            import_info = ImportInfo(
                module=alias.name,
                names=[],
                alias=alias.asname,
                is_from_import=False
            )
            self.imports.append(import_info)
        self.generic_visit(node)
        
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Besuche from...import statements."""
        if node.module:
            names = [alias.name for alias in node.names]
            import_info = ImportInfo(
                module=node.module,
                names=names,
                is_from_import=True
            )
            self.imports.append(import_info)
        self.generic_visit(node)
        
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Besuche Klassendefinitionen."""
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
        
        class_info = ClassInfo(
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
        
        # Temporär die aktuelle Klasse setzen für Methodenverarbeitung
        old_class = self.current_class
        self.current_class = class_info
        self.classes.append(class_info)
        
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Besuche Funktionsdefinitionen."""
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
        
        func_info = FunctionInfo(
            name=node.name,
            args=args,
            decorators=decorators,
            docstring=docstring,
            line_number=node.lineno,
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
        """Besuche async Funktionsdefinitionen."""
        args = [arg.arg for arg in node.args.args]
        
        decorators = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            else:
                decorators.append(ast.unparse(decorator))
                
        docstring = ast.get_docstring(node)
        
        func_info = FunctionInfo(
            name=node.name,
            args=args,
            decorators=decorators,
            docstring=docstring,
            line_number=node.lineno,
            is_async=True
        )
        
        if self.current_class:
            self.current_class.methods.append(func_info)
        else:
            self.functions.append(func_info)
            
        self.generic_visit(node)
        
    def visit_Assign(self, node: ast.Assign) -> None:
        """Besuche Zuweisungen für Konstanten."""
        # Nur Modul-Level Konstanten erfassen (UPPER_CASE)
        if not self.current_class:
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.isupper():
                    self.constants.append(target.id)
        self.generic_visit(node)

class MastermapGenerator:
    """Hauptklasse für die Generierung der Mastermap."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.engine_path = self.project_root / "engine"
        self.files: Dict[str, FileInfo] = {}
        
    def analyze_file(self, file_path: Path) -> Optional[FileInfo]:
        """Analysiert eine einzelne Python-Datei."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            analyzer = CodeAnalyzer()
            analyzer.visit(tree)
            
            # Zeilenzahl zählen
            line_count = len(content.splitlines())
            
            # Module docstring
            docstring = ast.get_docstring(tree)
            
            relative_path = str(file_path.relative_to(self.project_root))
            
            file_info = FileInfo(
                path=str(file_path),
                relative_path=relative_path,
                line_count=line_count,
                imports=analyzer.imports,
                classes=analyzer.classes,
                functions=analyzer.functions,
                constants=analyzer.constants,
                docstring=docstring
            )
            
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
                continue  # Skip __init__.py files
                
            file_info = self.analyze_file(py_file)
            if file_info:
                self.files[file_info.relative_path] = file_info
                
    def generate_module_summary(self) -> Dict[str, Any]:
        """Generiert eine Zusammenfassung der Module."""
        modules = defaultdict(list)
        
        for file_path, file_info in self.files.items():
            # Extrahiere Modul-Pfad (z.B. "engine/core", "engine/systems/battle")
            path_parts = Path(file_path).parts
            if len(path_parts) >= 2:
                module_path = "/".join(path_parts[:-1])  # Ohne Dateiname
                modules[module_path].append(file_info)
                
        return dict(modules)
    
    def generate_statistics(self) -> Dict[str, int]:
        """Generiert Statistiken über das Projekt."""
        stats = {
            'total_files': len(self.files),
            'total_lines': sum(f.line_count for f in self.files.values()),
            'total_classes': sum(len(f.classes) for f in self.files.values()),
            'total_functions': sum(len(f.functions) for f in self.files.values()),
            'total_methods': sum(sum(len(c.methods) for c in f.classes) for f in self.files.values()),
            'total_imports': sum(len(f.imports) for f in self.files.values()),
        }
        
        # Module-spezifische Statistiken
        modules = self.generate_module_summary()
        for module_name, files in modules.items():
            module_key = module_name.replace('/', '_')
            stats[f'{module_key}_files'] = len(files)
            stats[f'{module_key}_classes'] = sum(len(f.classes) for f in files)
            stats[f'{module_key}_functions'] = sum(len(f.functions) for f in files)
            
        return stats
    
    def generate_markdown_report(self) -> str:
        """Generiert einen vollständigen Markdown-Report."""
        modules = self.generate_module_summary()
        stats = self.generate_statistics()
        
        markdown = []
        
        # Header
        markdown.append("# Untold Story - Automatisch Generierte Code-Analyse")
        markdown.append("")
        markdown.append("## 📊 Gesamt-Statistiken")
        markdown.append("")
        markdown.append(f"- **Dateien:** {stats['total_files']}")
        markdown.append(f"- **Zeilen:** {stats['total_lines']:,}")
        markdown.append(f"- **Klassen:** {stats['total_classes']}")
        markdown.append(f"- **Funktionen:** {stats['total_functions']}")
        markdown.append(f"- **Methoden:** {stats['total_methods']}")
        markdown.append(f"- **Imports:** {stats['total_imports']}")
        markdown.append("")
        
        # Module-Übersicht
        markdown.append("## 🏗️ Module-Übersicht")
        markdown.append("")
        
        for module_path in sorted(modules.keys()):
            files = modules[module_path]
            module_name = module_path.replace('/', ' › ')
            
            markdown.append(f"### {module_name} ({len(files)} Dateien)")
            markdown.append("")
            
            # Tabelle mit Datei-Übersicht
            markdown.append("| Datei | Zeilen | Klassen | Funktionen | Beschreibung |")
            markdown.append("|-------|--------|---------|------------|--------------|")
            
            for file_info in sorted(files, key=lambda x: x.relative_path):
                filename = Path(file_info.relative_path).name
                desc = file_info.docstring.split('\n')[0] if file_info.docstring else "Keine Beschreibung"
                desc = desc.replace('|', '\\|')  # Escape pipes für Markdown-Tabellen
                
                markdown.append(f"| `{filename}` | {file_info.line_count} | {len(file_info.classes)} | {len(file_info.functions)} | {desc[:50]}{'...' if len(desc) > 50 else ''} |")
            
            markdown.append("")
        
        # Detaillierte Datei-Analyse
        markdown.append("## 🔍 Detaillierte Code-Analyse")
        markdown.append("")
        
        for module_path in sorted(modules.keys()):
            files = modules[module_path]
            module_name = module_path.replace('/', ' › ')
            
            markdown.append(f"### {module_name}")
            markdown.append("")
            
            for file_info in sorted(files, key=lambda x: x.relative_path):
                filename = Path(file_info.relative_path).name
                markdown.append(f"#### `{filename}` ({file_info.line_count} Zeilen)")
                
                if file_info.docstring:
                    markdown.append("")
                    markdown.append(f"**Beschreibung:** {file_info.docstring}")
                
                # Imports
                if file_info.imports:
                    markdown.append("")
                    markdown.append("**Imports:**")
                    markdown.append("```python")
                    for imp in file_info.imports:
                        if imp.is_from_import:
                            names_str = ", ".join(imp.names)
                            markdown.append(f"from {imp.module} import {names_str}")
                        else:
                            alias_str = f" as {imp.alias}" if imp.alias else ""
                            markdown.append(f"import {imp.module}{alias_str}")
                    markdown.append("```")
                
                # Konstanten
                if file_info.constants:
                    markdown.append("")
                    markdown.append(f"**Konstanten:** {', '.join(file_info.constants)}")
                
                # Klassen
                if file_info.classes:
                    markdown.append("")
                    markdown.append("**Klassen:**")
                    for cls in file_info.classes:
                        bases_str = f"({', '.join(cls.bases)})" if cls.bases else ""
                        decorators_str = f"@{', @'.join(cls.decorators)} " if cls.decorators else ""
                        
                        markdown.append(f"- `{decorators_str}{cls.name}{bases_str}` (Zeile {cls.line_number})")
                        
                        if cls.docstring:
                            markdown.append(f"  - {cls.docstring.split('.')[0]}.")
                        
                        if cls.methods:
                            method_names = [f"`{m.name}()`" for m in cls.methods[:5]]
                            if len(cls.methods) > 5:
                                method_names.append(f"... (+{len(cls.methods)-5} weitere)")
                            markdown.append(f"  - **Methoden:** {', '.join(method_names)}")
                        
                        if cls.properties:
                            prop_names = [f"`{p.name}`" for p in cls.properties]
                            markdown.append(f"  - **Properties:** {', '.join(prop_names)}")
                
                # Standalone-Funktionen
                if file_info.functions:
                    markdown.append("")
                    func_names = [f"`{f.name}()`" for f in file_info.functions]
                    markdown.append(f"**Funktionen:** {', '.join(func_names)}")
                
                markdown.append("")
        
        return "\n".join(markdown)
    
    def save_analysis_json(self, output_path: str) -> None:
        """Speichert die Analyse als JSON für weitere Verarbeitung."""
        data = {
            'statistics': self.generate_statistics(),
            'modules': self.generate_module_summary(),
            'files': {path: {
                'path': info.path,
                'relative_path': info.relative_path,
                'line_count': info.line_count,
                'docstring': info.docstring,
                'imports': [
                    {
                        'module': imp.module,
                        'names': imp.names,
                        'alias': imp.alias,
                        'is_from_import': imp.is_from_import
                    } for imp in info.imports
                ],
                'classes': [
                    {
                        'name': cls.name,
                        'bases': cls.bases,
                        'decorators': cls.decorators,
                        'docstring': cls.docstring,
                        'line_number': cls.line_number,
                        'methods': [m.name for m in cls.methods],
                        'properties': [p.name for p in cls.properties]
                    } for cls in info.classes
                ],
                'functions': [func.name for func in info.functions],
                'constants': info.constants
            } for path, info in self.files.items()}
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """Hauptfunktion."""
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = "."
    
    print(f"🔍 Analysiere Projekt: {project_root}")
    
    try:
        generator = MastermapGenerator(project_root)
        generator.scan_directory()
        
        print(f"✅ {len(generator.files)} Dateien analysiert")
        
        # Statistiken ausgeben
        stats = generator.generate_statistics()
        print(f"📊 Gesamt: {stats['total_files']} Dateien, {stats['total_lines']:,} Zeilen, {stats['total_classes']} Klassen")
        
        # Markdown-Report generieren
        markdown_report = generator.generate_markdown_report()
        
        # Report speichern
        output_path = Path(project_root) / "code_analysis_report.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_report)
        
        print(f"📝 Report gespeichert: {output_path}")
        
        # JSON für weitere Verarbeitung
        json_path = Path(project_root) / "code_analysis.json"
        generator.save_analysis_json(str(json_path))
        
        print(f"🔧 JSON-Daten gespeichert: {json_path}")
        
        return markdown_report, generator
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return None, None

if __name__ == "__main__":
    main()

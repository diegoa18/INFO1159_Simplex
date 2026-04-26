from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TableManager:
	# esta variable guarda la carpeta donde se guardaran los archivos de salida
	directorio_salida: Path

	def __init__(self, output_dir: str | Path = "outputs/tableado") -> None:
		ruta_convertida = Path(output_dir)
		# en self guardamos los datos que se usaran en otros metodos de la clase
		self.directorio_salida = ruta_convertida

	def obtener_directorio_salida(self) -> Path:
		# devuelve la carpeta configurada para guardar resultados
		return self.directorio_salida


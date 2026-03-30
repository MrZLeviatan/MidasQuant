# Importar todos los algoritmos
from .quick_sort import QuickSort
from .heap_sort import HeapSort
from .selection_sort import SelectionSort
from .comb_sort import CombSort
from .gnome_sort import GnomeSort
from .binary_insertion_sort import BinaryInsertionSort
from .tree_sort import TreeSort
from .tim_sort import TimSort
from .bucket_sort import BucketSort
from .pigeonhole_sort import PigeonholeSort
from .radix_sort import RadixSort
from .bitonic_sort import BitonicSort

# Definir exportación pública
__all__ = [
    "QuickSort",
    "HeapSort",
    "SelectionSort",
    "CombSort",
    "GnomeSort",
    "BinaryInsertionSort",
    "TreeSort",
    "TimSort",
    "BucketSort",
    "PigeonholeSort",
    "RadixSort",
    "BitonicSort",
]


# Simplifica brutalmente el orquestador
def get_all_algorithms():
    return {
        "TimSort": TimSort(),
        "Comb Sort": CombSort(),
        "Selection Sort": SelectionSort(),
        "Tree Sort": TreeSort(),
        "Pigeonhole Sort": PigeonholeSort(),
        "Bucket Sort": BucketSort(),
        "QuickSort": QuickSort(),
        "HeapSort": HeapSort(),
        "Bitonic Sort": BitonicSort(),
        "Gnome Sort": GnomeSort(),
        "Binary Insertion Sort": BinaryInsertionSort(),
        "Radix Sort": RadixSort(),
    }

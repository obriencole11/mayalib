import pymel.core as pmc
import logging

class UndoOnError(object):

    def __enter__(self):
        pmc.undoInfo(openChunk=True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pmc.undoInfo(closeChunk=True)
        if exc_val is not None:
            try:
                pmc.undo()
            except RuntimeError:
                pass
        if exc_type == AssertionError:
            logging.warning(exc_val)
            return True
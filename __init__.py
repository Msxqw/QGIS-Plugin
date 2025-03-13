def classFactory(iface):
    from .plugin import InvertGeometry
    return InvertGeometry(iface)

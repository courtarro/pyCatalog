# Enumerations
class MediaType:
    _empty, Movie, Music = range(3)

class ExternalIdProvider:
    _empty, UPC, Amazon, IMDB, CDDB = range(5)
    
class CoverType:
    _empty, Front, Back = range(3)

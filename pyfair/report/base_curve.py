from ..utility.fair_exception import FairException


class FairBaseCurve(object):
    '''Base class useful only for the ._input_check() method
    
    The distribution curve and exceedence curves provided in the report module
    both have a private _input_check() function and a public generate_image()
    function. The _input_check() function is shared and is consequently defined
    here. The generate_image() function is generated by the subclass and
    consequently raises a NotImplementedError.

    '''

    def _input_check(self, value):
        """Checks the input for compatability with curve
        
        Raises
        ------
        FairException
            Where the input is not a 1) FairModel, 2) FairMetaModel, or 3) an 
            iterable containing solely FairModels or FairMetaModels.
        
        """
        # If it's a model or metamodel, plug it in a dict.
        rv = {}
        if value.__class__.__name__ in ['FairModel', 'FairMetaModel']:
            rv[value.get_name()] = value
            return rv
        # Check for iterable. If not, raise error.
        if not hasattr(value, '__iter__'):
            raise FairException('Input is not a FairModel, FairMetaModel, or an iterable.')
        # Make sure not an empty iterable
        else:
            if len(value) == 0:
                raise FairException('Input is an empty iterable.')
        # Iterate and process remainder.
        for proported_model in value:
            if proported_model.__class__.__name__ in ['FairModel', 'FairMetaModel']:
                rv[proported_model.get_name()] = proported_model
            else:
                raise FairException('Iterable member is not a FairModel or FairMetaModel')
        return rv

    def generate_image(self):
        """Stub that raises a NotImpelmentedError
        
        Raises
        ------
        NotImplementedError
            In all circumstances because this function should be defined by the
            subclass.
        
        """
        raise NotImplementedError()

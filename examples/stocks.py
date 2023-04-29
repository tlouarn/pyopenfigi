from pyopenfigi import MappingJob, OpenFigi

# Instantiate the wrapper
wrapper = OpenFigi()

# Return a MappingJobResultFigiList where `data` contains many elements
# corresponding to all the listings of the IBM stock
mapping_job = MappingJob(id_type="TICKER", id_value="IBM")
results = wrapper.map([mapping_job])

# Return a MappingJobResultFigiList where `data` contains 1 element
mapping_job = MappingJob(id_type="TICKER", id_value="IBM", exch_code="UN")
results = wrapper.map([mapping_job])

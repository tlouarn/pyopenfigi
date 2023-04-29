from pyopenfigi import MappingJob, OpenFigi

# Instantiate the wrapper
wrapper = OpenFigi()

# Return a MappingJobFigiList for all the listings of the IBM SEP23 165 CALL
mapping_job = MappingJob(id_type="TICKER", id_value="IBM 09/15/23 C165")
results = wrapper.map([mapping_job])

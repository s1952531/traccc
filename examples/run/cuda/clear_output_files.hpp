#include <iostream>
#include <vector>
#include <string>
#include <fstream>

//a function to clear the output files
void clear_output_files()
{
    //make a list of all files to clear
    std::vector<std::string> files_to_clear = {
        "Plotting/ClusterizationData/clusters.csv",

        "Plotting/SeedingData/FilteredSeeds.csv",
        "Plotting/SeedingData/UnfilteredSeeds.csv",

        "Plotting/SeedingData/r_bin_borders.csv",
        "Plotting/SeedingData/phi_bin_borders.csv",
        "Plotting/SeedingData/z_bin_borders.csv",

        "Plotting/SeedingData/sp.csv",
        
        "Plotting/TrackParams/reconstructedTPs.csv",
        "Plotting/TrackParams/truthTPs.csv"
    };

    // clear output files if they exist
    for (const auto& file : files_to_clear) {
        std::ofstream ofs(file, std::ios::out);
        ofs.close();
    }
}
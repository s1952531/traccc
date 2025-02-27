#include <iostream>

void write_output_headers()
{
    std::ofstream clusterDataFile("Plotting/ClusterizationData/clusters.csv", std::ios_base::app);
    clusterDataFile << "cluster_index, module_index, channel0, channel1" << std::endl;
    clusterDataFile.close();

    std::ofstream filteredSeedsFile("Plotting/SeedingData/FilteredSeeds.csv", std::ios_base::app);
    filteredSeedsFile << "spB_x, spB_y, spB_z, spM_x, spM_y, spM_z, spT_x, spT_y, spT_z, weight, z_vertex" << std::endl;
    filteredSeedsFile.close();

    std::ofstream unfilteredSeedsFile("Plotting/SeedingData/UnfilteredSeeds.csv", std::ios_base::app);
    unfilteredSeedsFile << "spB_x, spB_y, spB_z, spM_x, spM_y, spM_z, spT_x, spT_y, spT_z, weight, z_vertex" << std::endl;
    unfilteredSeedsFile.close();

    std::ofstream rBinBordersFile("Plotting/SeedingData/r_bin_borders.csv", std::ios_base::app);
    rBinBordersFile << "r_bin_borders" << std::endl;
    rBinBordersFile.close();

    std::ofstream phiBinBordersFile("Plotting/SeedingData/phi_bin_borders.csv", std::ios_base::app);
    phiBinBordersFile << "phi_bin_border_start, phi_bin_border_end" << std::endl;
    phiBinBordersFile.close();

    std::ofstream zBinBordersFile("Plotting/SeedingData/z_bin_borders.csv", std::ios_base::app);
    zBinBordersFile << "z_bin_border_start, z_bin_border_end" << std::endl;
    zBinBordersFile.close();

    std::ofstream spCoordsFile("Plotting/SeedingData/sp.csv", std::ios_base::app);
    spCoordsFile << "sp_x, sp_y, sp_z" << std::endl;
    spCoordsFile.close();

    std::ofstream recoTPsFile("Plotting/TrackParams/reconstructedTPs.csv", std::ios_base::app);
    recoTPsFile << "global track dir params: x, y, z; phi, phi_var, theta, theta_var; spB_x, spB_y, spB_z, spM_x, spM_y, spM_z, spT_x, spT_y, spT_z" << std::endl;
    recoTPsFile.close();

    std::ofstream truthTPsFile("Plotting/TrackParams/truthTPs.csv", std::ios_base::app);
    truthTPsFile << "global track dir params: x, y, z; phi, phi_var, theta, theta_var" << std::endl;
    truthTPsFile.close();

}

void write_event_header(std::size_t event)
{
    std::vector<std::string> files_to_write = {
        "Plotting/ClusterizationData/clusters.csv",

        "Plotting/SeedingData/FilteredSeeds.csv",
        "Plotting/SeedingData/UnfilteredSeeds.csv",

        // "Plotting/SeedingData/r_bin_borders.csv",
        // "Plotting/SeedingData/phi_bin_borders.csv",
        // "Plotting/SeedingData/z_bin_borders.csv",

        "Plotting/SeedingData/sp.csv",
        
        "Plotting/TrackParams/reconstructedTPs.csv",
        "Plotting/TrackParams/truthTPs.csv"
    };

    for (const auto& file : files_to_write) {
        std::ofstream ofs(file, std::ios::app);
        ofs << std::endl << "Event: " << event << std::endl;
        ofs.close();
    }
}
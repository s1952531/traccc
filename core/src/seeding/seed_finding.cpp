/** TRACCC library, part of the ACTS project (R&D line)
 *
 * (c) 2021-2022 CERN for the benefit of the ACTS project
 *
 * Mozilla Public License Version 2.0
 */

// Library include(s).
#include "traccc/seeding/seed_finding.hpp"

#include <iostream>
#include <fstream>


namespace traccc {

// function to write the seed triplets to a file
void writeUnfilteredSeeds(const triplet_collection_types::host& triplets_per_spM, const sp_grid& g2) {
    std::cout << "\t\t\t\t\t\tNumber of unfiltered triplets" << triplets_per_spM.size() << std::endl;
    
    std::ofstream seedsFile;
    seedsFile.open("Plotting/SeedingData/UnfilteredSeeds.csv", std::ios_base::app);
    //for (unsigned int i = 0; i < triplets_per_spM.size(); i++) {
    for (const triplet& triplet : triplets_per_spM) {
        // const auto& spB_idx = triplet.sp1;
        // const auto& spB = g2.bin(spB_idx.bin_idx)[spB_idx.sp_idx];
        auto& spB = g2.bin(triplet.sp1.bin_idx)[triplet.sp1.sp_idx];
        auto& spM = g2.bin(triplet.sp2.bin_idx)[triplet.sp2.sp_idx];
        auto& spT = g2.bin(triplet.sp3.bin_idx)[triplet.sp3.sp_idx];
        
        seedsFile 
            << spB.x() << "," << spB.y() << "," << spB.z() << ","
            << spM.x() << "," << spM.y() << "," << spM.z() << ","
            << spT.x() << "," << spT.y() << "," << spT.z() << ","
            //<< triplet.curvature << "," // curvature not in seed struct (i.e. after filter to seed) so not writing it out
            << triplet.weight << "," 
            << triplet.z_vertex 
            << std::endl;

    }
    seedsFile.close();
}

// function to write the filtered seeds to a file
void writeFilteredSeeds(const seed_collection_types::host& seeds, const spacepoint_collection_types::host& sp_collection) {
    std::cout << "\t\t\t\t\t\tNumber of filtered seeds" << seeds.size() << std::endl;
    
    std::ofstream seedsFile;
    seedsFile.open("Plotting/SeedingData/FilteredSeeds.csv", std::ios_base::app);
    for (unsigned int i = 0; i < seeds.size(); i++) {
        //auto& spB1 = sp_collection.at(seed1.spB_link);
        auto& spB = sp_collection.at(seeds[i].spB_link);
        auto& spM = sp_collection.at(seeds[i].spM_link);
        auto& spT = sp_collection.at(seeds[i].spT_link);
        
        seedsFile 
        << spB.x() << "," << spB.y() << "," << spB.z() << ","
        << spM.x() << "," << spM.y() << "," << spM.z() << ","
        << spT.x() << "," << spT.y() << "," << spT.z() << ","
        << seeds[i].weight << "," 
        << seeds[i].z_vertex 
        << std::endl;
    }
    seedsFile.close();
}

seed_finding::seed_finding(const seedfinder_config& finder_config,
                           const seedfilter_config& filter_config)
    : m_midBot_finding(finder_config),
      m_midTop_finding(finder_config),
      m_triplet_finding(finder_config),
      m_seed_filtering(filter_config) {}

seed_finding::output_type seed_finding::operator()(
    const spacepoint_collection_types::host& sp_collection,
    const sp_grid& g2) const {

    std::cout << "\t\t(inside seed_finding.cpp)" << std::endl;

    // Run the algorithm
    output_type seeds;

    std::cout << "\t\tfor each bin get the spacepoints inside, get doublets then triplet" << std::endl;
    for (unsigned int i = 0; i < g2.nbins(); i++) {
        std::cout << "\t\t\tbin " << i << std::endl;
        auto& spM_collection = g2.bin(i); //

        //for each spacepoint in the middle bin
        for (unsigned int j = 0; j < spM_collection.size(); ++j) {
            std::cout << "\t\t\t\tsp {" << i << ", " << j << "}" << std::endl;
            sp_location spM_location({i, j});

            // middule-bottom doublet search
            auto mid_bot = m_midBot_finding(g2, spM_location);

            if (mid_bot.first.empty())
                continue;

            // middule-top doublet search
            auto mid_top = m_midTop_finding(g2, spM_location);

            if (mid_top.first.empty())
                continue;

            triplet_collection_types::host triplets_per_spM;

            // triplet search from the combinations of two doublets which
            // share middle spacepoint
            for (unsigned int k = 0; k < mid_bot.first.size(); ++k) {
                auto& doublet_mb = mid_bot.first[k];
                auto& lb = mid_bot.second[k];

                triplet_collection_types::host triplets = m_triplet_finding(
                    g2, doublet_mb, lb, mid_top.first, mid_top.second);

                triplets_per_spM.insert(std::end(triplets_per_spM),
                                        triplets.begin(), triplets.end());
            }

            // write unfiltered seeds i.e. triplets_per_spM to csv file
            writeUnfilteredSeeds(triplets_per_spM, g2);

            // seed filtering
            m_seed_filtering(sp_collection, g2, triplets_per_spM, seeds);

            // write filtered seeds i.e. seeds to csv file
            writeFilteredSeeds(seeds, sp_collection);
        }
    }

    //write seeds to csv file
    // std::ofstream seedsFile;
    // seedsFile.open("seeds.csv", std::ios_base::app);
    // for (unsigned int i = 0; i < seeds.size(); i++) {
    //     seedsFile << seeds[i].spB_link.x() << "," << seeds[i].spB_link.y() << "," << seeds[i].spB_link.z() << ","
    //               << seeds[i].spM_link.x() << "," << seeds[i].spM_link.y() << "," << seeds[i].spM_link.z() << ","
    //               << seeds[i].spT_link.x() << "," << seeds[i].spT_link.y() << "," << seeds[i].spT_link.z() << ","
    // }
    // seedsFile.close();

    return seeds;
}

}  // namespace traccc

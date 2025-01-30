/** TRACCC library, part of the ACTS project (R&D line)
 *
 * (c) 2022-2024 CERN for the benefit of the ACTS project
 *
 * Mozilla Public License Version 2.0
 */

// Library include(s).
#include "traccc/clusterization/sparse_ccl_algorithm.hpp"

#include "traccc/clusterization/details/sparse_ccl.hpp"
#include "traccc/sanity/contiguous_on.hpp"
#include "traccc/sanity/ordered_on.hpp"
#include "traccc/utils/projections.hpp"
#include "traccc/utils/relations.hpp"

// VecMem include(s).
#include <vecmem/containers/device_vector.hpp>
#include <vecmem/containers/vector.hpp>

//io for investigation
#include <iostream>
#include <filesystem>
#include <fstream>

namespace traccc::host {

    sparse_ccl_algorithm::sparse_ccl_algorithm(vecmem::memory_resource& mr)
        : m_mr(mr) {}

    sparse_ccl_algorithm::output_type sparse_ccl_algorithm::operator()(
        const edm::silicon_cell_collection::const_view& cells_view) const {

    std::cout << "\t(inside sparse_ccl_algorithm.cpp)" << std::endl;

    // Construct the device view of the cells.
    std::cout << "\t" << "Constructing the device view of the cells" << std::endl;
    const edm::silicon_cell_collection::const_device cells{cells_view};

    std::cout << "\t" << "Running some sanity checks on the cells" << std::endl;
    // Run some sanity checks on it.
    assert(is_contiguous_on(cell_module_projection(), cells));
    assert(is_ordered_on(channel0_major_cell_order_relation(), cells));

    std::cout << "\t" << "Running SparseCCL on the cells" << std::endl;
    // Run SparseCCL to fill CCL indices.
    vecmem::vector<unsigned int> cluster_indices{cells.size(), &(m_mr.get())};
    vecmem::device_vector<unsigned int> cluster_indices_device{
        vecmem::get_data(cluster_indices)};
    const unsigned int num_clusters =
        details::sparse_ccl(cells, cluster_indices_device);

    std::cout << "\t" << "Creating the result container" << std::endl;
    // Create the result container.
    output_type clusters{m_mr.get()}; //output type is edm::silicon_cluster
    clusters.resize(num_clusters);

    std::cout << "\t" << "Adding cells to their clusters" << std::endl;
    std::cout << "\t" << "Number of triggered cells: " << cluster_indices.size() << std::endl;
    std::cout << "\t" << "Number of clusters: " << num_clusters << std::endl;
    // Add cells to their clusters.
    for (unsigned int cell_idx = 0; cell_idx < cluster_indices.size();
         ++cell_idx) {
        clusters.cell_indices()[cluster_indices[cell_idx]].push_back(cell_idx);


        //if (cell_idx < 2){
        // std::cout << "\t" << "Adding cell " << cell_idx << " to cluster " << cluster_indices[cell_idx] << std::endl;
        // std::cout << "\t" << "Cell " << cell_idx << " has channel0 " << cells.channel0()[cell_idx] << std::endl;
        // std::cout << "\t" << "Cell " << cell_idx << " has channel1 " << cells.channel1()[cell_idx] << std::endl;
        // std::cout << "\t" << "Cell " << cell_idx << " has activation " << cells.activation()[cell_idx] << std::endl;
        // std::cout << "\t" << "Cell " << cell_idx << " has time " << cells.time()[cell_idx] << std::endl;
        // std::cout << "\t" << "Cell " << cell_idx << " has module_index " << cells.module_index()[cell_idx] << std::endl;

        std::filesystem::path file_path;
        // Write cluster data to respective event file
        //size_t event_idx = 0;
        // do {
        //     file_path = "ClusterizationData/event" + std::to_string(event_idx) + ".csv";
        //     event_idx++;
        // } while (std::filesystem::exists(file_path));  // Increment until a non-existing file is found
        file_path = "Plotting/ClusterizationData/test.csv";

        // Open the file for writing
        std::ofstream myfile;
        myfile.open(file_path, std::ios_base::app);

        // If the file is empty, write the header
        if (std::filesystem::file_size(file_path) == 0) {
            myfile << "cluster,module_index,channel0,channel1\n";
        }

        // Write the data
        myfile << cluster_indices[cell_idx] << ","
            << cells.module_index()[cell_idx] << "," 
            << cells.channel0()[cell_idx] << "," 
            << cells.channel1()[cell_idx] << "\n";

        myfile.close();

        //}      
        
    }
    
    std::cout << "\t" << "Returning the clusters" << std::endl;
    
    // Return the clusters.
    return clusters;
}

}  // namespace traccc::host

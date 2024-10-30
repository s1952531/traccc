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

namespace traccc::host {

sparse_ccl_algorithm::sparse_ccl_algorithm(vecmem::memory_resource& mr)
    : m_mr(mr) {}

sparse_ccl_algorithm::output_type sparse_ccl_algorithm::operator()(
    const edm::silicon_cell_collection::const_view& cells_view) const {

    std::cout << "calling ca()" << std::endl;

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
    output_type clusters{m_mr.get()};
    clusters.resize(num_clusters);

    std::cout << "\t" << "Adding cells to their clusters" << std::endl;
    // Add cells to their clusters.
    for (unsigned int cell_idx = 0; cell_idx < cluster_indices.size();
         ++cell_idx) {
        clusters.cell_indices()[cluster_indices[cell_idx]].push_back(cell_idx);
    }

    std::cout << "\t" << "Returning the clusters" << std::endl;
    // Return the clusters.
    return clusters;
}

}  // namespace traccc::host
